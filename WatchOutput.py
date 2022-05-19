# Watcher Test
# ------------
# Author: Beat Temperli
import pygame
import math
import os
import dotenv


# WatchOutput
# -----------
# Output of the watcher.
# Builds a screen with the current messages
# Updates the screen when a new message is ready for the output.
#
# Usage:
#
# from WatchOutput import WatchOutput
# watch_output = WatchOutput()
# watch_output.add_message('address', 'message')
class WatchOutput:

    # Init function
    # -------------
    # - Prepare pygame
    # - Prepare elements
    def __init__(self):
        super().__init__()

        dotenv.load_dotenv()

        self.pg = pygame
        self.pg.init()
        self.pg.font.init()
        self.pg.mouse.set_visible(False)

        self.screen = self.pg.display.set_mode((0, 0), self.pg.FULLSCREEN)
        self.display_info = pygame.display.Info()

        self.pg.display.set_caption('LoRaWatcher')
        self.show_screen = False
        self.small_font = self.pg.font.Font(os.environ.get('watcher-dir') + 'Asap.ttf', 20)
        self.small_font_line_height = 20
        self.color_light = (220, 220, 220)
        self.color_dark = (35, 35, 35)
        self.color_warning = (220, 220, 35)
        self.color_success = (35, 220, 70)
        self.color_danger = (220, 35, 35)
        self.color_main = (64, 123, 138)
        self.box_margin = 20
        self.header_height = 40
        self.box_main_x = self.box_margin
        self.box_main_y = self.box_margin
        self.box_main_width = self.display_info.current_w
        self.box_main_height = self.display_info.current_h

        # prepare elements
        self.box_background = self.pg.Rect(0, 0, self.box_main_width, self.box_main_height)
        self.button_quit = self.pg.Rect(self.box_main_width - self.box_margin - self.header_height,
                                        self.box_main_y,
                                        self.header_height,
                                        self.header_height)
        self.text_quit = self.small_font.render('x', True, self.color_light)
        self.text_box_quit = self.text_quit.get_rect(center=self.button_quit.center)

        # draw all needed elements
        self.__draw_display()

        self.address_set = set([])
        self.message_dict = {}

    # add a message to the system
    # id: string, address of the sender
    # message: string, message which was sent by sender
    def add_message(self, id, message):
        # add id if unknown till now.
        if id not in self.address_set:
            self.__add_address(id)

        self.message_dict[id].append(message)
        self.__display_messages()

    # Run
    # ---
    # Thread-based function to start the watcher.
    def run(self):
        print('run WatchOutput.py')
        self.__start()

    # draw display
    # ------------
    # draw all needed elements to the display
    def __draw_display(self):
        # boxes
        self.pg.draw.rect(self.screen, self.color_main, self.box_background)
        self.pg.draw.rect(self.screen, self.color_dark, self.button_quit)

        # text
        self.screen.blit(self.text_quit, self.text_box_quit)

        # show all recent changes
        self.pg.display.flip()

    # Get Grid
    # --------
    # Prepare the grid based on the current messages in "self.message_dict".
    # Builds a grid with max 4 columns
    def __get_grid(self):
        cols = field_count = len(self.message_dict)
        if cols > 4:
            cols = 4
        rows = math.ceil(field_count / cols)
        max_height = self.box_main_height - self.header_height - self.box_margin * 2
        col_width = (self.box_main_width - (cols + 1) * self.box_margin) // cols
        row_height = (max_height - rows * self.box_margin) // rows

        grid = []
        addresses = list(self.message_dict.keys())

        # calculate position for all grid fields
        for i in range(0, field_count):
            i_x = i % cols
            i_y = i // cols
            position_x = self.box_margin + i_x * col_width + i_x * self.box_margin
            position_y = self.header_height + self.box_margin * 2 + i_y * row_height + i_y * self.box_margin
            title = addresses[i]
            grid.append([position_x, position_y, col_width, row_height, title])

        return grid

    # update grid
    # -----------
    # - calculate position for all boxes
    # - draw the boxes to the display
    def __update_grid(self):
        grid = self.__get_grid()

        # redraw empty screen
        self.__draw_display()

        # create a box for all grid-fields
        for field in grid:
            field_box = self.pg.Rect(field[0], field[1], field[2], field[3])
            title = self.small_font.render(field[4], True, self.color_main)
            title_box = self.pg.Rect(field[0], field[1], field[2], self.header_height)
            title_box_subline = self.pg.Rect(field[0] + self.box_margin,
                                             field[1] + self.header_height,
                                             field[2] - self.box_margin * 2,
                                             3)
            title_text_box = title.get_rect(center=title_box.center)
            self.pg.draw.rect(self.screen, self.color_light, field_box)
            self.pg.draw.rect(self.screen, self.color_main, title_box_subline)
            self.screen.blit(title, title_text_box)

        # show boxes
        self.pg.display.flip()

    # Start
    # -----
    # - Start the mainloop
    # - Handle all click & key events
    def __start(self):
        while True:
            for event in self.pg.event.get():
                # keys
                if event.type == self.pg.KEYDOWN:
                    if event.key == self.pg.K_ESCAPE:
                        exit()

                # clicks
                if event.type == self.pg.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos  # gets mouse position

                    if self.button_quit.collidepoint(mouse_pos):
                        exit()

                # exit event
                if event.type == self.pg.QUIT:
                    exit()

    # Add address
    # -----------
    # Add a new address to the system
    def __add_address(self, id):
        self.address_set.add(id)
        self.message_dict[id] = []
        self.__update_grid()

    # display messages
    # ----------------
    # show all messages on the screen
    def __display_messages(self):
        grid = self.__get_grid()

        # create a box for all grid-fields
        for field in grid:
            start = field[1] + self.box_margin + self.header_height
            field_box = self.pg.Rect(field[0] + self.box_margin,
                                     start,
                                     field[2] - self.box_margin * 2,
                                     field[3] - self.box_margin * 2 - self.header_height)
            self.pg.draw.rect(self.screen, self.color_light, field_box)

            messages_index = len(self.message_dict[field[4]])
            for message in reversed(self.message_dict[field[4]]):
                text = self.small_font.render(str(messages_index) + ' ' + message, True, self.color_dark)
                text_box = self.pg.Rect(field[0] + self.box_margin,
                                        start + 2,
                                        field[2] - self.box_margin * 2,
                                        self.header_height)
                self.screen.blit(text, text_box)
                start += self.header_height
                messages_index -= 1

                # reached end of the box?
                if start + self.header_height > field[1] + field[3]:
                    break

            self.pg.display.flip()
