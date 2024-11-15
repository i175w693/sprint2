'''
Module Name: game.py
Purpose: This module is the main game code for the Cookie clicker game.
Inputs: None
Output: None
Additional code sources: 
Developers: Ian Wilson, Andrew Uriell, Peter Pham, Michael Oliver, Jack Youngquist
Date: 10/24/2024
Last Modified: 10/27/2024
'''

import pygame
import sys
import time

# imports necessary functions and classes from the other python files
from shop import shop_items, shop_upgrades
from cookie import Cookie
from save_game import save
from load_game import load
from sound import SoundManager
from cursor import Cursor

# Initialize pygame's video system
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)  # Color for partition lines
BUTTON_COLOR = (100, 100, 255)  # Color for buttons

# directory for accessing the assets for the game
ASSETS_FILEPATH = './assets'

# gets the font for rendering text
def get_font(size):
    return pygame.font.SysFont(None, size)

from buttons import Button, SmallButton, LargeButton

# UIManager class responsible for rendering the screen of the game and handling some of the backend such as shop items and user balances
class UIManager:
    def __init__(self):
        self.WIDTH = pygame.display.Info().current_w # sets the width to the current window's width for calculation purposes
        self.HEIGHT = pygame.display.Info().current_h # sets the height to the current window's height for calculation purposes
        self.cookie_count = 0
        self.upgrades_acquired = []
        # initializes the shop's items
        self.shop_items = shop_items
        # initializes the shop's upgrades
        self.shop_upgrades = shop_upgrades
        # Set up screen to dynamically fetch the display's width and height
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)  # Allows resizing
        pygame.display.set_caption("Cookie Clicker")
        self.buttons = self.create_buttons() # renders the buttons on the screen
        self.font_size = int(self.WIDTH * 0.03)  # Dynamic font size based on width
        self.font = get_font(self.font_size)
        self.show_main_menu = True
        self.show_saves_menu = False
        self.show_settings_popup = False
        self.main_menu_buttons = self.create_main_menu_buttons()  # Initialize with buttons
        self.save_button = SmallButton(self.WIDTH - int(self.WIDTH * 0.1), self.HEIGHT - int(self.HEIGHT * 0.1), "Save")
        self.sound_manager = SoundManager()
        self.no_cursor = pygame.mouse.set_visible(False)
        self.base_cookie_per_click = 1 # Start with 1 base cookie per click
        self.click_multiplier = 1.0     # Multiplier starts at 1.0 (no effect initially)
        self.cookie_per_click = self.base_cookie_per_click * self.click_multiplier
        self.scroll_offset = 0  # Initialize scroll offset
        self.max_scroll_offset = 0  # Initialize max scroll offset
        self.scroll_speed = 20  # Initialize scroll speed

    """Check if a specific button was clicked based on label and mouse position."""
    def button_clicked(self, label, mouse_pos):
        self.sound_manager.play_sound("menu-click")
        for button in self.main_menu_buttons:
            if button.text == label and button.is_clicked(mouse_pos):
                return True
        return False
    
    """Create main menu buttons and positions them on the screen."""
    def create_main_menu_buttons(self):
        button_labels = [("Continue", 'assets/menu/continue_button/continue_button_rectangle2.png'),
                         ("New Game", 'assets/menu/new_button/new_button_rectangle1.png'),
                         ("Settings", 'assets/menu/options_button/options_button_rectangle2.png'),
                         ("Exit", 'assets/menu/exit_button/exit_button_rectangle2.png')]
        buttons = []
        # renders each button on the screen with hardcoded position coordinates
        for idx, label in enumerate(button_labels):
            y_pos = int(self.HEIGHT * 0.2) + idx * int(self.HEIGHT * 0.18)
            button_width = int(self.WIDTH * 0.3)
            button_height = int(self.HEIGHT * 0.2)
            x_pos = (self.WIDTH - button_width) // 2
            button = LargeButton(self.screen, x_pos, y_pos, label[0], button_width, button_height, label[1])
            buttons.append(button)
        return buttons
    
    # Function to draw text
    def draw_text(self, text, font, color, x, y):
        text_obj = font.render(text, True, color)
        self.screen.blit(text_obj, (x, y)) # blit is used to draw an object onto the screen

    # function to render the buttons on the screen for each of the shop's items
    def create_buttons(self):
        buttons = []
        all_shop_items = {**shop_items, **shop_upgrades}
        button_height = int(self.HEIGHT * 0.05)
        button_margin = int(self.HEIGHT * 0.01)  # Add a margin between buttons
        total_height = len(all_shop_items) * (button_height + button_margin)
        self.max_scroll_offset = max(0, total_height - int(self.HEIGHT * 0.8))  # Calculate max scroll offset

        for idx, (k, v) in enumerate(all_shop_items.items()):
            button_width = int(self.WIDTH * 0.15)
            button_y = int(self.HEIGHT * 0.15) + idx * (button_height + button_margin) - self.max_scroll_offset
            button = LargeButton(self.screen, 
                                 self.WIDTH - int(self.WIDTH * 0.25), 
                                 button_y, 
                                 v.name, button_width, button_height)
            buttons.append((button, v))
        return buttons

    # function to handle to cookies earned per click
    def handle_cookie_click(self):
        self.cookie_count += self.cookie_per_click
        self.sound_manager.play_sound("click")
        # print(f"Cookie clicked! Total cookies: {self.cookie_count}")  # Log message for cookie clicks

    # function to handle the purchase of upgrades from the shop
    def handle_shop_click(self, mouse_pos):
        for button, item in self.buttons:
            if button.is_clicked(mouse_pos):
                # Calculate the current price
                current_price = int(item.base_cost * (1.15 ** item.purchased_count))

                # Only proceed if the player has enough cookies
                if self.cookie_count >= current_price:
                    # Lock the purchase process
                    self.processing_purchase = True
                    
                    # Deduct the cookie count and update purchase state
                    self.cookie_count -= current_price
                    item.purchased_count += 1  # Increment the purchase count

                    # Add the item to upgrades_acquired if not already in the list
                    if item not in self.upgrades_acquired:
                        self.upgrades_acquired.append(item)
                    
                    # Update button text with the new calculated price
                    button.text = f"{item.name} - ${int(item.base_cost * (1.15 ** item.purchased_count))} cookies"

                    # Apply any effects (CPC or CPS) associated with the item
                    if item.name.startswith("Click Multiplier"):
                        self.click_multiplier *= item.cpc
                    elif item.name.startswith("Increase Click"):
                        self.base_cookie_per_click += item.cpc
                    elif item.cpc is not None:
                        self.base_cookie_per_click += item.cpc
                    
                    # Recalculate cookies per click
                    self.cookie_per_click = self.base_cookie_per_click * self.click_multiplier
                    self.sound_manager.play_sound("shop")

                    # Unlock the purchase process
                    self.processing_purchase = False
    
    def handle_save_click(self):
        self.sound_manager.play_sound("menu-click")

    # returns the amount of cookies the user should be earning per second based on the purchased items
    def cookies_per_second(self):
        return sum(item.cps * item.purchased_count for item in self.shop_items.values() if item.cps != None)
    
    # This function isn't actually used anywhere in the code, but it's here if we want to use it in the future, it was messing with the upgrade implementation
    # returns the amount of cookies the user should be earning for each click based on their purchased items
    def cookies_per_click(self):
        pass
        # # Calculate the base cookies per click from purchased items
        # base_cpc = sum(item.cpc * item.purchased_count for item in self.shop_items.values() if item.cpc is not None)  
        # # If no items affecting CPC are purchased, set the base to 1
        # if base_cpc == 0:
        #     base_cpc = 1
        # # Apply the click multiplier to the base cookies per click
        # self.cookie_per_click = base_cpc * self.click_multiplier

    # renders the user's balance on the top left of the screen
    def draw_stats(self, screen):
        self.draw_text(f"Cookies: {self.cookie_count:.3f} (+{self.cookie_per_click:.3f} per click)", self.font, BLACK, int(self.WIDTH * 0.01), int(self.HEIGHT * 0.01))

    # renders the purchased item's to the middle column (will be replaced with sprites in the future).
    def draw_upgrades(self, screen):
        font_size = int(self.WIDTH * 0.03)  # Dynamic font size based on width
        font = get_font(font_size)
        self.draw_text("Upgrades Acquired:", font, BLACK, int(self.WIDTH * 0.4), int(self.HEIGHT * 0.05))
        if self.upgrades_acquired:
            for idx, upgrade in enumerate(self.upgrades_acquired):
                if upgrade.cpc is None:
                    self.draw_text(f"{upgrade.name} (CPS: {upgrade.cps}): {upgrade.purchased_count}", font, BLACK, int(self.WIDTH * 0.4), int(self.HEIGHT * 0.15) + idx * int(self.HEIGHT * 0.05))
                else:
                    self.draw_text(f"{upgrade.name} (CPC: {upgrade.cpc}): {upgrade.purchased_count}", font, BLACK, int(self.WIDTH * 0.4), int(self.HEIGHT * 0.15) + idx * int(self.HEIGHT * 0.05))


    # draws the shop section of the screen
    def draw_shop(self, screen):
        font_size = int(self.WIDTH * 0.03)
        font = get_font(font_size)
        self.draw_text("Shop:", font, BLACK, int(self.WIDTH * 0.75), int(self.HEIGHT * 0.05))
        
        # Draw shop items
        for button, item in self.buttons:
            if 0 <= button.y <= self.HEIGHT:  # Only draw buttons within the visible area
                button.draw(screen)
            current_price = int(item.base_cost * (1.15 ** item.purchased_count))
            button.text = f"{item.name} - {current_price} cookies"
            button.draw(screen)

        # Draw scroll bar
        self.draw_scroll_bar(screen)

    # Draws vertical lines to partition the screen
    def draw_partitions(self, screen):
        pygame.draw.line(screen, GRAY, (self.WIDTH * 0.33, 0), (self.WIDTH * 0.33, self.HEIGHT), 2)  # Left partition
        pygame.draw.line(screen, GRAY, (self.WIDTH * 0.66, 0), (self.WIDTH * 0.66, self.HEIGHT), 2)  # Right partition    

    # renders the main menu screen when the user starts the game
    def draw_main_menu(self):
        # Draw the title
        title_font = get_font(int(self.HEIGHT * 0.1))
        self.draw_text("KU Cookie Clicker", title_font, BLACK, self.WIDTH // 2 - title_font.size("KU Cookie Clicker")[0] // 2, int(self.HEIGHT * 0.1))

        # Draw menu buttons
        for button in self.main_menu_buttons:
            button.draw(self.screen)

    # draws buttons onto the screen (currently unused)
    def draw_button(self, label, y_pos):
        # Button properties
        button_width = int(self.WIDTH * 0.4)
        button_height = int(self.HEIGHT * 0.08)
        x_pos = (self.WIDTH - button_width) // 2

        # Draw button rectangle
        pygame.draw.rect(self.screen, BUTTON_COLOR, (x_pos, y_pos, button_width, button_height))

        # Draw button text
        button_font = get_font(int(button_height * 0.5))
        text_surface = button_font.render(label, True, WHITE)
        text_x = x_pos + (button_width - text_surface.get_width()) // 2
        text_y = y_pos + (button_height - text_surface.get_height()) // 2
        self.screen.blit(text_surface, (text_x, text_y))

    # placeholder for rendering the save slots screen
    def draw_save_slots(self):
        pass

    # renders the settings screen
    def draw_settings_popup(self):
        # Draw settings background
        popup_width = int(self.WIDTH * 0.5)
        popup_height = int(self.HEIGHT * 0.5)
        popup_x = (self.WIDTH - popup_width) // 2
        popup_y = (self.HEIGHT - popup_height) // 2
        pygame.draw.rect(self.screen, GRAY, (popup_x, popup_y, popup_width, popup_height))

        # Settings sliders and labels
        settings_font = get_font(int(popup_height * 0.1))
        self.draw_text("Settings", settings_font, BLACK, popup_x + popup_width // 2 - settings_font.size("Settings")[0] // 2, popup_y + 10)

        # Draw slider bars and labels
        labels = ["Music", "SFX"]
        for i, label in enumerate(labels):
            y_pos = popup_y + int(popup_height * 0.3) + i * int(popup_height * 0.2)
            self.draw_slider(label, popup_x + int(popup_width * 0.1), y_pos, popup_width, popup_height)

    # renders the sliders used in the settings menu
    def draw_slider(self, label, x, y, popup_width, popup_height):
        slider_width = int(popup_width * 0.6)
        slider_height = int(popup_height * 0.1)

        # Draw label
        slider_font = get_font(int(slider_height * 0.5))
        text_surface = slider_font.render(label, True, BLACK)
        self.screen.blit(text_surface, (x, y))

        # Draw slider bar
        pygame.draw.rect(self.screen, BLACK, (x + int(popup_width * 0.2), y, slider_width, slider_height // 5))

        # Draw mute checkbox
        checkbox_side = slider_height
        checkbox_x = x + int(popup_width * 0.8)
        checkbox_y = y
        pygame.draw.rect(self.screen, BLACK, (checkbox_x, checkbox_y, checkbox_side, checkbox_side))
        
    def draw_scroll_bar(self, screen):
        bar_width = int(self.WIDTH * 0.02)
        bar_height = int(self.HEIGHT * 0.8)
        bar_x = self.WIDTH - bar_width - 10
        bar_y = int(self.HEIGHT * 0.15)
        
        # Draw the scroll bar background
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Calculate the scroll handle position
        handle_height = max(20, bar_height * (bar_height / (bar_height + self.max_scroll_offset)))
        
        # Prevent division by zero
        if self.max_scroll_offset > 0:
            handle_y = bar_y + (self.scroll_offset / self.max_scroll_offset) * (bar_height - handle_height)
        else:
            handle_y = bar_y  # Default position if no scrolling is needed
        
        # Draw the scroll handle
        pygame.draw.rect(screen, BLACK, (bar_x, handle_y, bar_width, handle_height))

    def run_main_menu(self):
        # Display either the main menu, saves, or settings based on flags
        if self.show_main_menu:
            self.draw_main_menu()
        elif self.show_saves_menu:
            self.draw_save_slots()
        elif self.show_settings_popup:
            self.draw_settings_popup()

    def handle_events(self):
        for event in pygame.event.get():
            ...
            # Handle mouse wheel scrolling
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_offset -= event.y * self.scroll_speed
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll_offset))
            ...

    def start_new_game(self):
        # Reset cookie count and upgrades
        self.cookie_count = 0
        self.upgrades_acquired = []

        # Reset each shop item's purchase count and price
        for item in self.shop_items.values():
            item.purchased_count = 0
            item.cost = item.base_cost  # Reset to the initial base price

        # Reset each shop upgrade's purchase count and price
        for upgrade in self.shop_upgrades.values():
            upgrade.purchased_count = 0
            upgrade.cost = upgrade.base_cost  # Reset to the original price

        # Reset cookies per click and multiplier
        self.base_cookie_per_click = 1
        self.click_multiplier = 1.0
        self.cookie_per_click = self.base_cookie_per_click * self.click_multiplier

        # Reset any other game-related state, such as showing main menu or other flags
        self.show_main_menu = False

# Main game class
class Game:
    # initializes the UI and time keeping functions
    def __init__(self):
        self.ui_manager = UIManager()
        self.cookie = Cookie(f"{ASSETS_FILEPATH}/cookie.png", 0.2, self.ui_manager.WIDTH, self.ui_manager.HEIGHT)
        self.last_time = time.time()
        self.clock = pygame.time.Clock()
        self.cursor = Cursor(f"{ASSETS_FILEPATH}/cursor/cursor1.png", 1, 64, 64)

    # checks each event that occurs in pygame and updates the game accordingly.
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save(self.ui_manager)
                elif event.key == pygame.K_l:
                    load(self.ui_manager)
                elif event.key == pygame.K_ESCAPE:
                    self.ui_manager.show_main_menu = not self.ui_manager.show_main_menu
            
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
            
                if self.ui_manager.show_main_menu:
                    # Handle main menu button clicks
                    if self.ui_manager.button_clicked("Continue", mouse_pos):
                        self.ui_manager = UIManager() # recreates a new UIManager to populate with the save file's data
                        # Load the game state when Continue is clicked
                        if load(self.ui_manager) == None: # if a save file doesnt exist, create a new save
                            self.ui_manager = UIManager() # recreates a new UIManager with empty stats
                            self.ui_manager.show_main_menu = False
                        else: # else load the save file
                            self.ui_manager.show_main_menu = False  # Hide the main menu after loading
                    elif self.ui_manager.button_clicked("New Game", mouse_pos):
                        self.ui_manager.start_new_game()  # Start a new game with initial values
                        self.ui_manager.show_main_menu = False
                    elif self.ui_manager.button_clicked("Settings", mouse_pos):
                        self.ui_manager.show_settings_popup = True
                    elif self.ui_manager.button_clicked("Exit", mouse_pos):
                        pygame.quit()
                        sys.exit()
                else:
                    # Handle game-related clicks
                    if self.cookie.rect.collidepoint(mouse_pos):
                        self.ui_manager.handle_cookie_click()
                        self.ui_manager.draw_text(f"+{self.ui_manager.cookie_per_click:.3f}", self.ui_manager.font, BLACK, int(mouse_pos[0]-26), int(mouse_pos[1]-30))
                    
                    # Check if save button is clicked - IMPORTANT make this a function 
                    if self.ui_manager.save_button.is_clicked(mouse_pos):
                        self.ui_manager.handle_save_click()
                        save(self.ui_manager)  # Call save function

                    self.ui_manager.handle_shop_click(mouse_pos)

            # Handle window resizing
            if event.type == pygame.VIDEORESIZE:
                self.ui_manager.WIDTH, self.ui_manager.HEIGHT = event.w, event.h
                self.ui_manager.screen = pygame.display.set_mode((self.ui_manager.WIDTH, self.ui_manager.HEIGHT), pygame.RESIZABLE)
                self.cookie = Cookie(f"{ASSETS_FILEPATH}/cookie.png", 0.2, self.ui_manager.WIDTH, self.ui_manager.HEIGHT)
                self.ui_manager = UIManager()

            # Handle mouse wheel scrolling
            if event.type == pygame.MOUSEWHEEL:
                self.ui_manager.scroll_offset -= event.y * self.ui_manager.scroll_speed
                self.ui_manager.scroll_offset = max(0, min(self.ui_manager.scroll_offset, self.ui_manager.max_scroll_offset))

    # Begins the game and runs in a continuous loop
    def run(self):
        while True:
            self.ui_manager.screen.fill(WHITE)
            if self.ui_manager.show_main_menu:
                # Run main menu if the flag is set
                self.ui_manager.run_main_menu()
            else:
                # Run the main game loop if the menu is not active
                current_time = time.time()
                # updates the user's cookie balance based on their shop purchases
                if current_time - self.last_time >= 1:
                    self.ui_manager.cookie_count += self.ui_manager.cookies_per_second()
                    self.last_time = current_time

                # renders the various sections of the screen
                self.cookie.draw(self.ui_manager.screen)
                self.ui_manager.cookies_per_click()
                self.ui_manager.draw_stats(self.ui_manager.screen)
                self.ui_manager.draw_upgrades(self.ui_manager.screen)
                self.ui_manager.draw_shop(self.ui_manager.screen)
                self.ui_manager.draw_partitions(self.ui_manager.screen)
                self.cookie.update_rotation()

                # Draw the save button
                self.ui_manager.save_button.draw(self.ui_manager.screen)

            # Handle events and update display
            self.handle_events()
            # Handle cursor sprite movement
            self.cursor.update()
            self.cursor.draw()
            pygame.display.flip() # updates the screen in Pygame
            self.clock.tick(30) # limits the game to 30 ticks per second


