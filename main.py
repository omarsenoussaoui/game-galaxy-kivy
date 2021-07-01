import random

from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle

Builder.load_file('menu.kv')

class MainWidget(RelativeLayout):
    from transforms import transform , transform_2D ,transform_perspective
    from user_actions import on_keyboard_up , on_keyboard_down,on_touch_down,on_touch_up ,keyboard_closed

    menu_widget = ObjectProperty()
    menu_title = StringProperty("G A L A X Y")
    menu_button_title = StringProperty("START")
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    score_text = StringProperty()

    V_NB_LINES = 8
    V_LINES_SPACING = 0.4
    vertical_lines = []

    H_NB_LINES = 8
    H_LINES_SPACING = 0.1
    horizontal_lines = []


    SPEED  = 0.1
    current_offset_y = 0

    SPEED_X = 1.0
    current_speed_x = 0
    current_offset_x = 0
    current_y_loop = 0

    NB_TILES = 4
    tiles = []
    tiles_cordinates = []


    SHIP_WIDTH = 0.1
    SHIP_HEIGTH = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_cordinates = [(0,0) ,(0,0) , (0,0)]

    state_game_over = False
    state_game_start = False


    def __init__(self,**kwargs):
        super(MainWidget, self).__init__(**kwargs)
        #print("INIT W :" + str(self.width) + "H : " + str(self.height))
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def reset_game(self):

        self.current_offset_y = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.current_y_loop = 0
        self.menu_widget

        self.tiles_cordinates = []
        self.pre_fill_tiles_cordinates()
        self.generate_tiles_cordinates()
        self.state_game_over = False

    def is_desktop(self):
        if platform in ('linux' , 'win' , 'macosx') :
            return True
        return False

    def init_ship(self):
        with self.canvas:
            Color(0,0,0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width/2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGTH * self.height

        self.ship_cordinates[0] = (center_x - ship_half_width , base_y)
        self.ship_cordinates[1] = (center_x, base_y + ship_height)
        self.ship_cordinates[2] = (center_x + ship_half_width, base_y)

        x1 , y1 = self.transform(*self.ship_cordinates[0])
        x2, y2 = self.transform(*self.ship_cordinates[1])
        x3, y3 = self.transform(*self.ship_cordinates[2])
        self.ship.points = [x1,y1,x2,y2,x3,y3]

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_cordinates)):
            ti_x , ti_y = self.tiles_cordinates[i]
            if ti_x > self.current_y_loop + 1:
                return False
            if self.check_shipcollision_with_tile(ti_x,ti_y):
                return True
        return False



    def check_shipcollision_with_tile(self , ti_x , ti_y):
        xmin , ymin = self.get_tile_cordinates(ti_x,ti_y)
        xmax, ymax = self.get_tile_cordinates(ti_x + 1, ti_y + 1)

        for i in range(0 , 3):
            px , py = self.ship_cordinates[i]
            if xmin <= px <= xmax and  ymin <= py <= ymax :
                return  True
        return  False


    def init_tiles(self):
        with self.canvas:
            Color(1,1,1,0.75)
            for i in range(0,self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_cordinates(self):
        for i in range(0,10):
            self.tiles_cordinates.append((0,i))
    def generate_tiles_cordinates(self):
        last_x = 0
        last_y = 0


        for i in range(len(self.tiles_cordinates)-1,-1,-1):
            if self.tiles_cordinates[i][1] < self.current_y_loop :
                del self.tiles_cordinates[i]

        if len(self.tiles_cordinates) > 0 :
            last_cordinates = self.tiles_cordinates[-1]
            last_x = last_cordinates[0]
            last_y = last_cordinates [1] + 1

        for i in range(len(self.tiles_cordinates) , self.NB_TILES):
            r = random.randint(0,2)

            start_index = - int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1

            if last_x <= start_index :
                r= 1
            if last_x >= end_index :
                r = 2
            self.tiles_cordinates.append((last_x, last_y))
            if r == 1 :
                last_x += 1
                self.tiles_cordinates.append((last_x, last_y))
                last_y +=1
                self.tiles_cordinates.append((last_x, last_y))

            if r == 2 :
                last_x -= 1
                self.tiles_cordinates.append((last_x, last_y))
                last_y +=1
                self.tiles_cordinates.append((last_x, last_y))
            last_y += 1

    def init_vertical_lines(self):
        with self.canvas:
            Color(1,1,1,0.75)
            for i in range(0,self.V_NB_LINES):
                self.vertical_lines.append(Line())


    def get_line_x_from_index(self,index):
        center_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset =  index - 0.5
        line_x = center_line_x + offset*spacing +self.current_offset_x
        return  line_x


    def get_line_y_from_index(self,index):

        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y

        return line_y


    def get_tile_cordinates(self,ti_x,ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)

        return x , y

    def update_tiles(self):
        for i in range(0,self.NB_TILES):
            tile = self.tiles[i]
            tile_cordinates = self.tiles_cordinates[i]
            xmin , ymin = self.get_tile_cordinates(tile_cordinates[0],tile_cordinates[1])
            xmax, ymax = self.get_tile_cordinates(tile_cordinates[0] + 1, tile_cordinates[1]+ 1)

            x1 , y1 = self.transform(xmin , ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)


            tile.points = [x1,y1,x2,y2,x3,y3,x4,y4]


    def update_vertical_lines(self):
        start_index = - int(self.V_NB_LINES/2) + 1
        for i in range(start_index,start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1 , y1 = self.transform(line_x,0)
            x2 , y2 = self.transform(line_x,self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]


    def init_horizontal_lines(self):
        with self.canvas:
            Color(1,1,1,1)
            for i in range(0,self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):

        start_index = - int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        spacing_y = self.H_LINES_SPACING * self.height

        for i in range(0,self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1 , y1 = self.transform(xmin,line_y)
            x2 , y2 = self.transform(xmax,line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]



    def update(self,dt):
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        if not self.state_game_over and self.state_game_start:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y  * time_factor
            spacing_y = self.H_LINES_SPACING * self.height

            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop +=1
                self.score_text = 'SCORE : ' + str(self.current_y_loop)
                self.generate_tiles_cordinates()
                print(self.current_y_loop)
            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += self.current_speed_x * time_factor

        if not self.check_ship_collision() and not self.state_game_over :
            self.menu_button_title = "RESTART"
            self.menu_title = "G A M E     O V E R "
            self.state_game_over = True
            self.menu_widget.opacity = 1

    def on_menu_button_pressed(self):
        self.reset_game()
        self.state_game_start = True
        self.menu_widget.opacity = 0
class GalaxyApp(App):
    pass

GalaxyApp().run()