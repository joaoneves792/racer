from gi.repository import Gtk, Gdk, GLib
import cairo
import random
import math

import ParticleManager

# 1 meter = 36 pixels !!

class Window:
    WIDTH = 1024
    HEIGHT = 512
    
    VERSION = "v2.1"

class HUD:
    PLAYER2_DELTA_X = 800
    SCORE_POS_X = (50, 50+PLAYER2_DELTA_X)
    SCORE_POS_Y = (50, 50)
    TIME_OUT_POS_X = (50, 50+PLAYER2_DELTA_X)
    TIME_OUT_POS_Y = (70, 70)
    INVENTORY_X = (50, 50+PLAYER2_DELTA_X)
    INVENTORY_Y = (450, 450)
    POINTS100_X = (50, 50+PLAYER2_DELTA_X)
    POINTS100_SPEED_DIRECTION = (1, -1)

class KeyboardKeys:
    KEY_ESC = 65307
    KEY_LEFT  = (65361, 97)
    KEY_RIGHT = (65363,100)
    KEY_UP = (65362, 119)
    KEY_DOWN = (65364, 115)
    KEY_ONE = (49, 65457)
    KEY_FIVE = (54, 65461)
    KEY_TO_NUM = (KEY_ONE[0] - 1, KEY_ONE[1] - 1)

class RoadPositions:
    UPPER_LIMIT = 105
    LOWER_LIMIT = 404
    FORWARD_LIMIT = 912
    REAR_LIMIT = 0
    LEFT_LANE = 165
    MIDDLE_LANE = 260
    RIGHT_LANE = 355
    BEYOND_HORIZON = 1312
    BEHIND_REAR_HORIZON = -250
    COLLISION_HORIZON = Window.WIDTH + 100

class Speed:
    ONE_METER = 36
    KMH_TO_MS = 0.2777
    MS_TO_PMIL =  0.036 #m/s tp pixels per milisecond
    KMH_TO_PMIL = KMH_TO_MS*MS_TO_PMIL
    SIXTY_KMH = 60*KMH_TO_PMIL
    ONE_KMH = KMH_TO_PMIL
    ONE_RADMIL = 0.001 
    MAX_KMH = 80
    MAX_WOBBLE_ROTATION = 0.52359
    MAX_SPEED = MAX_KMH*ONE_KMH
    BASE_CRASH_SPEED_DECREASE = (10*ONE_KMH) 

class SkidMarks:
    SKID_LEFT = cairo.ImageSurface.create_from_png("skid_left.png")
    SKID_RIGHT= cairo.ImageSurface.create_from_png("skid_right.png")


class CarModels:
    GALLARDO_PLAYER1 = cairo.ImageSurface.create_from_png("./gallardo_player1.png")
    GALLARDO_PLAYER2 = cairo.ImageSurface.create_from_png("./gallardo_player2.png")
    CORVETTE = cairo.ImageSurface.create_from_png("corvette.png")
    AMBULANCE = cairo.ImageSurface.create_from_png("emergency.png")
    CHARGER = cairo.ImageSurface.create_from_png("./charger.png")
    GOLF = cairo.ImageSurface.create_from_png("./golf.png")
    INTEGRA = cairo.ImageSurface.create_from_png("./integra.png")
    SUPRA = cairo.ImageSurface.create_from_png("./supra.png")
    F430 = cairo.ImageSurface.create_from_png("./f430.png")
    CCX = cairo.ImageSurface.create_from_png("./ccx.png")
    COP = cairo.ImageSurface.create_from_png("./cop.png")
    DB9 = cairo.ImageSurface.create_from_png("./db9.png")
    F1 = cairo.ImageSurface.create_from_png("./f1.png")
    SUPERLEGGERA = cairo.ImageSurface.create_from_png("./gallardo_superleggera.png")
    GT = cairo.ImageSurface.create_from_png("./gt.png")
    LP570 = cairo.ImageSurface.create_from_png("./lp570.png")
    MURCIELAGO = cairo.ImageSurface.create_from_png("./murcielago.png")
    R8 = cairo.ImageSurface.create_from_png("./r8.png")
    RS4 = cairo.ImageSurface.create_from_png("./rs4.png")
    SL65 = cairo.ImageSurface.create_from_png("./sl65.png")
    SLR = cairo.ImageSurface.create_from_png("./slr.png")
    TRUCK_BLUE = cairo.ImageSurface.create_from_png("./truck_blue.png")
    TRUCK_RED = cairo.ImageSurface.create_from_png("./truck_red.png")
    TRUCK_GREEN = cairo.ImageSurface.create_from_png("./truck_green.png")

    AVAILABLE_CARS = ( CORVETTE, CHARGER, GOLF, INTEGRA, SUPRA, F430, CCX, DB9, F1, SUPERLEGGERA, GT, LP570, MURCIELAGO, R8, RS4, SL65, SLR )
    TRUCKS = ( TRUCK_GREEN, TRUCK_RED, TRUCK_BLUE )
    EMERGENCY_CARS = ( AMBULANCE, COP )

class PowerUps:
    TIME_OUT = 10000 #in miliseconds
    INVENTORY_SIZE = 5
    ICON_SIZE = 32
    EMPTY = cairo.ImageSurface.create_from_png("./empty.png")
    SHIELD = cairo.ImageSurface.create_from_png("./shield.png")
    ENERGY_SHIELD = cairo.ImageSurface.create_from_png("./energyshield.png")
    ENERGY_SHIELD_WIDTH = cairo.ImageSurface.get_width(ENERGY_SHIELD)
    ENERGY_SHIELD_HEIGHT = cairo.ImageSurface.get_height(ENERGY_SHIELD)
    HYDRAULICS = cairo.ImageSurface.create_from_png("./Hydraulics.png")
    CALL_911 = cairo.ImageSurface.create_from_png("./911.png")
    SHRINK = cairo.ImageSurface.create_from_png("./shrink.png")
    PHASER_FIRE = cairo.ImageSurface.create_from_png("./phaser_fire.png")
    PHASER = cairo.ImageSurface.create_from_png("./phaser.png")

class SmokeEmitter(ParticleManager.ParticleEmitter):
    def __init__(self, x, y, speed_x, speed_y):
        super(SmokeEmitter, self).__init__(x, y, speed_x, speed_y, 25, ParticleManager.Particles.SMOKE, 20, 0.1)
    def set_particles(self):
        for particle in self.particles:
            particle.set_properties(self.x, self.y, 500, math.pi/2, self.speed_x + random.randrange(-5, 5)*Speed.ONE_KMH, self.speed_y + random.randrange(-5, 5)*Speed.ONE_KMH,  self.size, self.shape, False)

class PointsEmitter(ParticleManager.ParticleEmitter):
    def __init__(self, x, y, speed_x, speed_y, size=100, shape=ParticleManager.Particles.POINTS, rate=0.1, num_of_particles=3):
        super(PointsEmitter, self).__init__(x, y, speed_x, speed_y, size, shape, num_of_particles , 0.1)
    def set_particles(self):
        for particle in self.particles:
            particle.set_properties(self.x, self.y, 700, 0, self.speed_x + random.randrange(-5, 5)*Speed.ONE_KMH, self.speed_y + random.randrange(-5, 5)*Speed.ONE_KMH,  self.size, self.shape, True)

class Minus10Points(PointsEmitter):
    def __init__(self, x, y, speed_x, speed_y, size=100, shape=ParticleManager.Particles.POINTS, num_of_particles=6):
        super(Minus10Points, self).__init__(x, y, speed_x, speed_y, size, shape, 0.01, num_of_particles)
    def set_particles(self):
        for particle in self.particles:
            particle.set_properties(self.x, self.y, 800, 0, self.speed_x + random.randrange(-5, 5)*Speed.ONE_KMH, self.speed_y + random.randrange(-5, 5)*Speed.ONE_KMH,  self.size, self.shape, True)


class Plus100Points(PointsEmitter):
    def __init__(self, x, speed):
        super(Plus100Points, self).__init__(x, 130, speed, 0.1, 200, ParticleManager.Particles.PLUS_100_POINTS, 1, 1)

class Minus100Points(PointsEmitter):
    def __init__(self, x, speed):
        super(Minus100Points, self).__init__(x, 130, speed,  0.1, 400, ParticleManager.Particles.MINUS_100_POINTS, 1, 1)

class MessageEmitter(ParticleManager.ParticleEmitter):
    def __init__(self, x, y, shape):
        super(MessageEmitter, self).__init__(x, y, 0, 0, 100, shape, 1, 1)
    def set_particles(self):
        for particle in self.particles:
            particle.set_properties(self.x, self.y, 1500, 0, self.speed_x, self.speed_y,  self.size, self.shape, True)

class HolyShit(MessageEmitter):
    def __init__(self):
        super(HolyShit, self).__init__(512, 340, ParticleManager.Particles.HOLY_SHIT)

class Mayhem(MessageEmitter):
    def __init__(self):
        super(Mayhem, self).__init__(512, 256, ParticleManager.Particles.MAYHEM)

class Annihilation(MessageEmitter):
    def __init__(self):
        super(Annihilation, self).__init__(512, 170, ParticleManager.Particles.ANNIHILATION)

class Road():
    def __init__(self, x=0):
        self.road = cairo.ImageSurface.create_from_png("road3.png")
        self.x = x; #x is the position on the screen
        self.width = 2048 #cairo.ImageSurface.get_width(self.road)
        self.height = cairo.ImageSurface.get_height(self.road)

    def draw(self, cr):
        cr.save()
        cr.translate(self.x-128, 0)
        cr.set_source_surface(self.road, 0, 0)
        cr.paint()
        
        cr.restore()

    def advance(self, amount):
        if self.x <= -int(self.width / 2):
            self.x = 0
        else:
            self.x -= amount

class Car:
    def __init__(self, model, x, y, speed):
        self.model = model
        self.vertical_position = y
        self.horizontal_position = x
        self.height = cairo.ImageSurface.get_height(model)
        self.width = cairo.ImageSurface.get_width(model)
        self.height_offset = self.height/2
        self.speed = speed
        self.rotation = 0

    #Not Here but you must implement an update and a draw method

    def check_collision(self, box_x, box_y, box_w, box_h, car):
            if ((box_x < car.horizontal_position + car.width) #if box is before end of car
                    and (box_x + box_w > car.horizontal_position) #if front of box is ahead of car back
                    and (box_y < car.vertical_position + car.height) #if box is below passanger side of car
                    and (box_y + box_h > car.vertical_position)): #if box overlaps car by the side
                return True
            else:
                return False

    def ahead(self, other):
        box_x = other.horizontal_position + other.width
        box_y = other.vertical_position
        box_h = other.height
        box_w = 250 #Distance to check for vehicles ahead
        return self.check_collision(box_x, box_y, box_w, box_h, self)

    def slower(self, other):
        return (self.speed < other.speed)


class Player(Car):
    def __init__(self, model, x, y, speed, player_id):
        super(Player, self).__init__(model, x, y, speed)
        self.player_id = player_id
        self.draw_rotation = False
        self.up = False
        self.down = False
        self.forward = False
        self.braking = False
        self.crash_handler = None
        self.score = 0
        self.score_hundreds = 0

        self.inventory = []
        self.powerUpTimeOut = 0
        self.hydraulics = False
        self.shield = False
        self.shrunk = False
        self.fire_phaser = False
        self.phaser_alpha = 0
        self.phaser_gaining_intensity = True

    def update(self, time_delta):
        for i in range(self.score_hundreds - int(self.score / 100)):
            ParticleManager.add_new_emmitter(Minus100Points(HUD.POINTS100_X[self.player_id], HUD.POINTS100_SPEED_DIRECTION[self.player_id]*Speed.MAX_SPEED))
        self.score += 0.01 * time_delta
        old_score_hundreds = self.score_hundreds
        self.score_hundreds = int(self.score / 100)
        for i in range(self.score_hundreds-old_score_hundreds):
            ParticleManager.add_new_emmitter(Plus100Points(HUD.POINTS100_X[self.player_id], HUD.POINTS100_SPEED_DIRECTION[self.player_id]*Speed.MAX_SPEED))
        #Adjust postition to user input
        if self.up and self.vertical_position > RoadPositions.UPPER_LIMIT + self.height_offset:
            self.vertical_position -= 5 if not self.shrunk else 2
        elif self.down and self.vertical_position < RoadPositions.LOWER_LIMIT - self.height_offset:
            self.vertical_position += 5 if not self.shrunk else 2
        
        if self.forward and self.horizontal_position < RoadPositions.FORWARD_LIMIT:
            self.horizontal_position += 5 if not self.shrunk else 2
        elif self.braking and self.horizontal_position > RoadPositions.REAR_LIMIT:
            self.horizontal_position -= 5 if not self.shrunk else 2

        if self.speed < Speed.MAX_SPEED:
            displacement = (Speed.MAX_SPEED - self.speed)*time_delta
            self.horizontal_position -= displacement if (self.horizontal_position - displacement) >= 0 else 0 

        if self.fire_phaser:
            if self.phaser_gaining_intensity:
                self.phaser_alpha += time_delta*0.005
                if self.phaser_alpha >= 1:
                    self.phaser_alpha = 1
                    self.phaser_gaining_intensity = False
            else:
                self.phaser_alpha -= time_delta*0.005
                if self.phaser_alpha <= 0:
                    self.phaser_alpha = 0
                    self.phaser_gaining_intensity = True
                    self.fire_phaser = False

        if(self.powerUpTimeOut > 0):
            self.powerUpTimeOut -= time_delta
        if self.powerUpTimeOut <= 0:
            self.disablePowerUps()
            self.powerUpTimeOut = 0

    def draw(self, cr):
        cr.save()
        cr.translate(self.horizontal_position, self.vertical_position - self.height_offset);
        if self.fire_phaser:
            cr.save()
            cr.translate(10, self.height_offset - 8)
            cr.set_source_surface(PowerUps.PHASER_FIRE, 0, 0)
            cr.paint_with_alpha(self.phaser_alpha)
            cr.restore()
        if self.draw_rotation:
            x = self.width/2.0
            y = self.height/2.0
            cr.translate(x, y)
            cr.rotate(self.rotation);
            cr.translate(-x,-y) 
        if self.hydraulics:
            cr.scale(1.2, 1.2)
        if self.shrunk:
            cr.scale(1, 0.5)
        cr.set_source_surface(self.model, 0, 0)
        cr.paint()
        if self.shield:
            cr.save()
            cr.translate(self.width/2 - PowerUps.ENERGY_SHIELD_WIDTH/2, self.height_offset - PowerUps.ENERGY_SHIELD_HEIGHT/2)
            cr.set_source_surface(PowerUps.ENERGY_SHIELD, 0, 0)
            cr.paint()
            cr.restore()
        cr.restore()
        
        if self.crash_handler != None:
            self.crash_handler.draw(cr)
       
        self.draw_score(cr)
        self.draw_power_up_timer(cr)
        self.draw_inventory(cr)

    def draw_score(self, cr):
        if(self.score > 0):
            cr.set_source_rgb(1, 1, 1)
        else:
            cr.set_source_rgb(1, 0, 0)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(20)
        cr.move_to(HUD.SCORE_POS_X[self.player_id], HUD.SCORE_POS_Y[self.player_id])
        cr.show_text("SCORE: " + str(int(self.score)))

    def draw_power_up_timer(self, cr):
        if self.powerUpTimeOut <= 0:
            return
        time_out_seconds = int(self.powerUpTimeOut / 1000)
        if(time_out_seconds > 3):
            cr.set_source_rgb(1, 1, 1)
        else:
            cr.set_source_rgb(1, 0, 0)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(20)
        cr.move_to(HUD.TIME_OUT_POS_X[self.player_id], HUD.TIME_OUT_POS_Y[self.player_id])
        cr.show_text("0:" + str(time_out_seconds))

    def draw_inventory(self, cr):
        for i in range(PowerUps.INVENTORY_SIZE):
            cr.save()
            x = HUD.INVENTORY_X[self.player_id]+PowerUps.ICON_SIZE*i
            cr.translate(x, HUD.INVENTORY_Y[self.player_id])
            if i < len(self.inventory):
                cr.set_source_surface(self.inventory[i].icon, 0, 0)
            else:
                cr.set_source_surface(PowerUps.EMPTY, 0, 0)

            if self.powerUpTimeOut > 0:
                cr.paint_with_alpha(0.5)
            else:
                cr.paint()

            cr.restore()

            if self.powerUpTimeOut == 0:
                cr.set_source_rgb(1, 1, 1)
            else:
                cr.set_source_rgb(1, 0, 0)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(14)
            cr.move_to(x + (PowerUps.ICON_SIZE/2)-7, HUD.INVENTORY_Y[self.player_id]+PowerUps.ICON_SIZE+20)
            cr.show_text(str(i+1))

    def addPowerUp(self, powerup):
        if len(self.inventory) < PowerUps.INVENTORY_SIZE:
            self.inventory.append(powerup)

    def usePowerUp(self, num):
        if(num <= len(self.inventory) and self.powerUpTimeOut == 0):
            self.inventory.pop(num-1).execute()

    def disablePowerUps(self):
        self.hydraulics = False
        self.shield = False
        self.shrunk = False
        self.height = cairo.ImageSurface.get_height(self.model)
        self.height_offset = self.height/2

class NPV(Car): #NPV - Non Player Vehicle
    def __init__(self, model, y, speed):
        super(NPV, self).__init__(model, RoadPositions.BEYOND_HORIZON, y, speed)
        self.angular_speed = 0      #NPV specific
        self.wobbling = False       #NPV specific
        self.wobbling_side = True #True = Left False=Right #NPV specific
        self.original_lane = self.vertical_position #NPV specific
        self.switching_to_left_lane = False   #NPV specific
        self.switching_to_right_lane = False  #NPV specific
        self.skiding = False                  #NPV specific
        self.skid_marks_x = 0                 #NPV specific
        self.skid_marks_y = 0                 #NPV specific
        self.skid_mark = None                 #NPV specific
        self.crashed = False

    def check_overtake_need(self, cars):
        if self.skiding or (self.switching_to_left_lane or self.switching_to_right_lane):
            return
        for car in cars:
            if car == self:
                continue
            if car.ahead(self) and car.slower(self):
                if not self.change_lane(cars):
                    self.match_speed_of(car)

    def change_lane(self, cars):
        self.original_lane = self.vertical_position
        if self.vertical_position == RoadPositions.LEFT_LANE and self.is_lane_free(cars, RoadPositions.MIDDLE_LANE):
            self.switching_to_right_lane = True
        elif self.vertical_position == RoadPositions.RIGHT_LANE and self.is_lane_free(cars, RoadPositions.MIDDLE_LANE):
            self.switching_to_left_lane = True
        elif self.vertical_position == RoadPositions.MIDDLE_LANE:        
            if random.randrange(2) == 0 and self.is_lane_free(cars, RoadPositions.LEFT_LANE):
                self.switching_to_left_lane = True
            elif self.is_lane_free(cars, RoadPositions.RIGHT_LANE):
                self.switching_to_right_lane = True
        if not (self.switching_to_left_lane or self.switching_to_right_lane):
            return False
        return True

    def is_lane_free(self, cars, lane):
        if len(cars) == 0:
            return True
        box_x = self.horizontal_position - 20; #begining of the car minus some clearance
        box_y = lane;   #Middle of the car
        box_w = self.width + 100 #give it some clearance
        box_h = self.height
        for car in cars:
            if car == self:
                continue
            if self.check_collision(box_x, box_y, box_w, box_h, car):
                return False
        return True

    def swerve(self):
        self.change_lane([]) #passing an empty list of other cars: doesnt check if lanes are free

    def match_speed_of(self, other_car):
        if self.speed < 0: #ignore if we are an ambulance
            return
        if other_car.speed > 0:
            if (other_car.horizontal_position - self.horizontal_position) < self.width+50:
                self.speed = other_car.speed
        else:
            self.speed = 0
            self.skiding = True
            self.skid_marks_x = self.horizontal_position - 50

    def hit_from_behind(self):
        if self.speed > 0:
            self.speed = (Speed.MAX_KMH - 5)*Speed.ONE_KMH
        elif self.speed == 0:
            self.speed = Speed.SIXTY_KMH
        elif self.speed < 0: #ambulances
            self.speed += 10*Speed.ONE_KMH
            
        if random.randrange(2) == 0:
            self.angular_speed += (0.5*Speed.ONE_RADMIL)
        else:
            self.angular_speed -= (0.3*Speed.ONE_RADMIL)
        self.skiding = True
        self.swerve()

    def wobble(self):
        self.wobbling = True
        self.wobbling_side = (random.randrange(2) == 0)
        self.skiding = True
        self.swerve()

    def draw(self, cr):
        if self.skid_mark != None:
            cr.save()
            cr.translate(self.skid_marks_x, self.skid_marks_y-self.height_offset)
            cr.set_source_surface(self.skid_mark, 0, 0)
            cr.paint()
            cr.restore()
        
        cr.save()
        cr.translate(self.horizontal_position, self.vertical_position - self.height_offset);
        x = self.width / 2.0
        y = self.height / 2.0
        cr.translate(x, y)
        cr.rotate(self.rotation)
        cr.translate(-x, -y)
        cr.set_source_surface(self.model, 0, 0)
        cr.paint()
        cr.restore()
    
    def update(self, time_delta, player_speed):
        horizontal_position_delta = time_delta*(self.speed-player_speed)
        self.horizontal_position += horizontal_position_delta 
        self.rotation += time_delta*self.angular_speed
        if self.rotation != 0:
            self.speed -= 1*Speed.ONE_KMH if self.speed > 3*Speed.ONE_KMH else 0
        
        if self.wobbling:
            if self.rotation >= Speed.MAX_WOBBLE_ROTATION or self.rotation <= -Speed.MAX_WOBBLE_ROTATION:
                self.wobbling_side = not self.wobbling_side
                self.angular_speed = 0
            if self.wobbling_side == True:
                self.angular_speed += 0.2*Speed.ONE_RADMIL
            else:
                self.angular_speed -= 0.2*Speed.ONE_RADMIL

        lateral_speed = int(5*(float(self.speed)/float(Speed.MAX_KMH*Speed.ONE_KMH)))
        if self.switching_to_left_lane:
            if self.original_lane == RoadPositions.RIGHT_LANE:
                if self.vertical_position <= RoadPositions.MIDDLE_LANE:
                    self.switching_to_left_lane = False
                    self.vertical_position = RoadPositions.MIDDLE_LANE
                else:
                    self.vertical_position -= lateral_speed
            else:
                if self.vertical_position <= RoadPositions.LEFT_LANE:
                    self.switching_to_left_lane = False
                    self.vertical_position = RoadPositions.LEFT_LANE
                else:
                    self.vertical_position -= lateral_speed
        elif self.switching_to_right_lane:
            if self.original_lane == RoadPositions.LEFT_LANE:
                if self.vertical_position >= RoadPositions.MIDDLE_LANE:
                    self.switching_to_right_lane = False
                    self.vertical_position = RoadPositions.MIDDLE_LANE
                else:
                    self.vertical_position += lateral_speed
            else:
                if self.vertical_position >= RoadPositions.RIGHT_LANE:
                    self.switching_to_right_lane = False
                    self.vertical_position = RoadPositions.RIGHT_LANE
                else:
                    self.vertical_position += lateral_speed
        if self.skiding:
            if self.skid_mark == None and self.switching_to_left_lane:
                self.skid_mark = SkidMarks.SKID_LEFT
            elif self.skid_mark == None and self.switching_to_right_lane:
                self.skid_mark = SkidMarks.SKID_RIGHT
            if self.skid_marks_y == 0:
                self.skid_marks_y = self.vertical_position
            if self.skid_marks_x == 0:
                self.skid_marks_x = self.horizontal_position
            else:
                self.skid_marks_x += time_delta*(-player_speed) 


class Truck(NPV):
    def __init__(self, model, y, speed, game):
            super(Truck, self).__init__(model, y, speed)
            self.game = game
            self.looted = False

    def update(self, time_delta, player_speed):
        if(self.horizontal_position < RoadPositions.FORWARD_LIMIT and random.randrange(200) == 1):
            self.dropPowerUp()
        if self.crashed and not self.looted:
            self.dropPowerUp()
            self.dropPowerUp()
            self.looted = True
        super(Truck, self).update(time_delta, player_speed)

    def dropPowerUp(self):
        rand = random.randrange(5)
        if rand == 0:
            Call911(self.game).drop(self.horizontal_position, self.vertical_position-self.height_offset)
        elif rand == 1:
            Hydraulics(self.game).drop(self.horizontal_position, self.vertical_position-self.height_offset)
        elif rand == 2:
            Shrink(self.game).drop(self.horizontal_position, self.vertical_position-self.height_offset)
        elif rand == 3:
            Phaser(self.game).drop(self.horizontal_position, self.vertical_position-self.height_offset)
        else:
            Shield(self.game).drop(self.horizontal_position, self.vertical_position-self.height_offset)

class PlayerCrashHandler:
    ACCELARATION = 0.000005
    def __init__(self, player, other_object_speed, other_object_mass = 10):
        self.t = 0
        self.player = player
        self.player.speed -= self.calculateSpeedDecrease(self.player.speed - other_object_speed, other_object_mass)
        self.player.forward = False
        jolt = self.calculateSideJolt(self.player.speed - other_object_speed, other_object_mass)
        self.player.vertical_position += jolt
        self.player.draw_rotation = True
        self.skid_mark = SkidMarks.SKID_LEFT if jolt < 0 else SkidMarks.SKID_RIGHT
        self.skid_marks_x = None
        self.skid_marks_y = None
        self.timeout = 1700

    def calculateSpeedDecrease(self, impact_speed, mass):
        if(impact_speed < 0.1):
            speedDecrease = Speed.BASE_CRASH_SPEED_DECREASE
        else:
            speedDecrease = Speed.BASE_CRASH_SPEED_DECREASE * impact_speed*mass
        if self.player.speed - speedDecrease <= 0:
            return self.player.speed
        else:
            return speedDecrease

    def calculateSideJolt(self, impact_speed, mass):
        #jolt = 20**(1+(impact_speed*mass*100)) #TODO Make me better
        jolt = 20
        if (random.randrange(2) == 0):
            if self.player.vertical_position > RoadPositions.UPPER_LIMIT+jolt+self.player.height_offset: 
                return -jolt 
            else:
                return RoadPositions.UPPER_LIMIT + self.player.height_offset - self.player.vertical_position
        else:
            if self.player.vertical_position < RoadPositions.LOWER_LIMIT-jolt-self.player.height_offset:
                return jolt
            else:
                return RoadPositions.LOWER_LIMIT - self.player.height_offset - self.player.vertical_position

    def update(self, time_delta):
        if(self.player.speed >= Speed.MAX_KMH*Speed.ONE_KMH):
            self.player.speed = Speed.MAX_KMH*Speed.ONE_KMH
            self.player.rotation = 0.0000001
            self.player.draw_rotation = False

        if self.player.speed < Speed.MAX_KMH*Speed.ONE_KMH:
            self.player.speed += self.t*self.ACCELARATION
        if self.player.draw_rotation:
            self.player.rotation = 2*math.sqrt(self.t+1)**(-1)*math.sin(0.05*self.t)


        if self.skid_marks_y == None:
            self.skid_marks_y = self.player.vertical_position
        if self.skid_marks_x == None:
            self.skid_marks_x = self.player.horizontal_position
        else:
            self.skid_marks_x += time_delta*(-Speed.MAX_SPEED) 

        self.t += time_delta
        if self.t >= self.timeout and self.player.draw_rotation == False:
            self.player.crash_handler = None

    def draw(self, cr):
        cr.save()
        cr.translate(self.skid_marks_x, self.skid_marks_y - self.player.height_offset)
        cr.set_source_surface(self.skid_mark, 0, 0)
        cr.paint()
        cr.restore()

class PowerUp:
    def __init__(self, game, player=None):
        self.player = player
        self.game = game    
        self.icon = PowerUps.EMPTY
        self.x = 0
        self.y = 0

    def drop(self, x, y):
        self.game.droped_items.append(self)
        self.x = x
        self.y = y

    def execute(self):
        if self.player == None:
            return
        self.player.powerUpTimeOut = PowerUps.TIME_OUT
        self.applyPowerUp()
    
    #abstract
    def applyPowerUp(self):
        pass

    def picked_up_by(self, player):
        self.game.droped_items.remove(self)
        self.player = player
        player.addPowerUp(self)

    def update(self, time_delta):
        self.x += time_delta*(-Speed.MAX_SPEED)
        if self.x < -PowerUps.ICON_SIZE:
            self.game.droped_items.remove(self)

    def draw(self, cr):
        cr.save()
        cr.translate(self.x, self.y)
        cr.set_source_surface(self.icon, 0, 0)
        cr.paint()
        cr.restore()


class Call911(PowerUp):
    def __init__(self, game, player=None):
        super(Call911, self).__init__(game, player)
        self.icon = PowerUps.CALL_911

    def applyPowerUp(self):
        self.game.generateEmergencyVehicle(self.player.vertical_position)

class Hydraulics(PowerUp):
    def __init__(self, game, player=None):
        super(Hydraulics, self).__init__(game, player)
        self.icon = PowerUps.HYDRAULICS

    def applyPowerUp(self):
        self.player.hydraulics = True

class Shield(PowerUp):
    def __init__(self, game, player=None):
        super(Shield, self).__init__(game, player)
        self.icon = PowerUps.SHIELD

    def applyPowerUp(self):
        self.player.shield = True

class Shrink(PowerUp):
    def __init__(self, game, player=None):
        super(Shrink, self).__init__(game, player)
        self.icon = PowerUps.SHRINK

    def applyPowerUp(self):
        self.player.shrunk = True
        self.player.height = self.player.height / 2
        self.player.height_offset = self.player.height_offset / 2

class Phaser(PowerUp):
    def __init__(self, game, player=None):
        super(Phaser, self).__init__(game, player)
        self.icon = PowerUps.PHASER

    def applyPowerUp(self):
        self.player.fire_phaser = True

class Game(Gtk.Window):

    def __init__(self):
        super(Game, self).__init__()
        self.init_ui()
        self.road = Road(0)
        self.speed = Speed.MAX_SPEED
        self.previous_crash_count = 0
        self.last_update_timestamp = -1
        self.npvs = []
        self.spawn_delay = 0
        self.players = []
        self.droped_items = []
        self.paused = True
        self.singlePlayer = True


        #self.players[0].addPowerUp(Call911(self, self.players[0]))
        #self.players[0].addPowerUp(Hydraulics(self, self.players[0]))
        #self.players[0].addPowerUp(Shield(self, self.players[0]))
        #self.players[0].addPowerUp(Call911(self, self.players[0]))


    def init_ui(self):
        self.grid = Gtk.Grid()
        box = Gtk.Box()

        play_button = Gtk.Button(label="Play")
        play_button.connect("clicked", self.start_new_game)
        single_multi_player = Gtk.ComboBoxText()
        single_multi_player.append_text("Singleplayer")
        single_multi_player.append_text("Multiplayer")
        single_multi_player.set_active(0)
        single_multi_player.connect("changed", self.changed_num_of_players)
        
        box.pack_start(single_multi_player, False, False, 0)
        box.pack_end(play_button, False, False, 0)
        
        self.grid.add(box)

        self.grid.set_orientation(Gtk.Orientation.VERTICAL)

        image = Gtk.Image.new_from_file("./Screenshot.png")
        
        self.grid.add(image)

        self.darea = Gtk.DrawingArea()
        self.set_title("GENERIC RACER!!! " + Window.VERSION)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.resize(Window.WIDTH, Window.HEIGHT)
        self.set_size_request(Window.WIDTH, Window.HEIGHT)
        self.connect("delete-event", Gtk.main_quit)
        self.add(self.grid)
        self.show_all()
        self.set_resizable(False)
  
    def start_new_game(self, button):
        self.remove(self.grid)
        self.add(self.darea)
        self.show_all() 
        self.players.append(Player(CarModels.GALLARDO_PLAYER1 , 0, RoadPositions.LEFT_LANE, Speed.MAX_SPEED, 0))
        if self.singlePlayer == False:
            self.players.append(Player(CarModels.GALLARDO_PLAYER2 , 0, RoadPositions.RIGHT_LANE, Speed.MAX_SPEED, 1))
        self.darea.connect("draw", self.on_draw)
        self.add_tick_callback(self.update)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.add_events(Gdk.EventMask.KEY_RELEASE_MASK)
        self.connect("key-press-event", self.on_key_press)
        self.connect("key-release-event", self.on_key_release)
        self.paused = False


    def changed_num_of_players(self, combo):
        text = combo.get_active_text()
        if text == "Singleplayer":
            self.singlePlayer = True
        else:
            self.singlePlayer = False

    def generateEmergencyVehicle(self, vertical_position):
            self.npvs.append(NPV(CarModels.EMERGENCY_CARS[random.randrange(len(CarModels.EMERGENCY_CARS))], vertical_position, -20*Speed.ONE_KMH))

    def generateRandomNPV(self):
        #Select a random lane
        random_num = random.randrange(3)
        if random_num == 0:
            lane = RoadPositions.LEFT_LANE
        elif random_num == 1:
            lane = RoadPositions.MIDDLE_LANE
        else:
            lane = RoadPositions.RIGHT_LANE

        #Select a Speed
        speed = Speed.MAX_SPEED - Speed.ONE_KMH*(random.randrange(20) + 5) # -5 beacause we need the npvs to always be slower than the player

        #Select a car
        random_num = random.randrange(100)
        if random_num < 4:
            self.generateEmergencyVehicle(lane)
        elif random_num < 10:
            self.npvs.append(Truck(CarModels.TRUCKS[random.randrange(len(CarModels.TRUCKS))], lane, speed, self))
        else:
            self.npvs.append(NPV(CarModels.AVAILABLE_CARS[random.randrange(len(CarModels.AVAILABLE_CARS))], lane, speed))

    def update(self, wid, fc):
        current_time = fc.get_frame_time()
        if self.last_update_timestamp == -1:
            self.last_update_timestamp = current_time
        time_delta = (current_time - self.last_update_timestamp)/1000 # frame time is in microseconds, we want miliseconds

        if self.paused:
            self.last_update_timestamp = current_time
            return True

        self.road.advance(time_delta*Speed.MAX_SPEED) #self.speed)

        for player in self.players:
            player.update(time_delta)

        #Update NPVs
        if self.spawn_delay > 0:
            self.spawn_delay -= time_delta
        #Delete NPVs that are behind us (not visible anymore)        
        for npv in self.npvs[:]:  #Mind the [:] its there so we iterate on a copy of the list
            if npv.horizontal_position <= RoadPositions.BEHIND_REAR_HORIZON:
                self.npvs.remove(npv)
                #Just a reminder this is only feasable because were using really small lists THIS DOES NOT SCALE WELL!!
        #create new NPVs
        if len(self.npvs) < 8:
            if self.spawn_delay <= 0:
                self.generateRandomNPV()
                self.spawn_delay = 900
        #Recalculate their position
        for npv in self.npvs:
            npv.check_overtake_need(self.npvs)
            npv.update(time_delta, self.speed)


        #Collision detection
        #(between player and non-players)
        for player in self.players:
            if player.hydraulics:
                continue
            for npv in self.npvs[:]:
                if self.check_collision(player.horizontal_position, player.vertical_position, player.width, player.height, npv.horizontal_position, npv.vertical_position, npv.width, npv.height):
                    npv.wobble()
                    if not player.shield:
                        if not npv.crashed:
                            ParticleManager.add_new_emmitter(Minus10Points(player.horizontal_position, player.vertical_position, -player.speed, 0.2))
                            player.score -= 60
                            if(player.crash_handler == None):
                                player.crash_handler = PlayerCrashHandler(player, npv.speed)
                    if not npv.crashed:
                        npv.crashed = True
                        ParticleManager.add_new_emmitter(SmokeEmitter( npv.horizontal_position, npv.vertical_position-npv.height_offset, -npv.speed, 0))
                if player.fire_phaser:
                    if self.check_collision(player.horizontal_position, player.vertical_position, RoadPositions.COLLISION_HORIZON, player.height, npv.horizontal_position, npv.vertical_position, npv.width, npv.height):
                        ParticleManager.add_new_emmitter(SmokeEmitter( npv.horizontal_position, npv.vertical_position-npv.height_offset, 0, 0))
                        self.npvs.remove(npv)

        #(between non-players themselves)
        for i in range(len(self.npvs) - 1):
            for j in range(i+1, len(self.npvs)):
                if self.check_collision(self.npvs[i].horizontal_position, self.npvs[i].vertical_position, self.npvs[i].width, self.npvs[i].height, self.npvs[j].horizontal_position, self.npvs[j].vertical_position, self.npvs[j].width, self.npvs[j].height):
                    self.npv_collision(self.npvs[i], self.npvs[j])


        #between players
        for i in range(len(self.players) - 1):
            for j in range(i+1, len(self.players)):
                if self.players[i].hydraulics or self.players[j].hydraulics:
                    continue
                if self.check_collision(self.players[i].horizontal_position, self.players[i].vertical_position, self.players[i].height, self.players[i].width, 
                                        self.players[j].horizontal_position, self.players[j].vertical_position, self.players[j].height, self.players[j].width):
                    if(self.players[i].crash_handler == None and not self.players[i].shield):
                        self.players[i].crash_handler = PlayerCrashHandler(self.players[i], self.players[j].speed)
                    if(self.players[j].crash_handler == None and not self.players[j].shield):
                        self.players[j].crash_handler = PlayerCrashHandler(self.players[j], self.players[i].speed)



        #Update Particle Emitters
        ParticleManager.update(time_delta)

        #Messages
        current_crashed_count = 0
        for npv in self.npvs:
            if npv.crashed:
                 current_crashed_count += 1

        if current_crashed_count > self.previous_crash_count:
            if current_crashed_count == 3:
                ParticleManager.add_new_emmitter(HolyShit())
            elif current_crashed_count == 4:
                ParticleManager.add_new_emmitter(Mayhem())
            elif current_crashed_count > 4:
                ParticleManager.add_new_emmitter(Annihilation())
            
        self.previous_crash_count = current_crashed_count

        for player in self.players:
            for item in self.droped_items:
                if self.check_collision(player.horizontal_position, player.vertical_position, player.width, player.height, item.x, item.y, PowerUps.ICON_SIZE, PowerUps.ICON_SIZE):
                    item.picked_up_by(player)


        for item in self.droped_items:
            item.update(time_delta)
            
        for player in self.players:    
            if player.crash_handler != None:
                player.crash_handler.update(time_delta)

        self.last_update_timestamp = current_time
        self.darea.queue_draw()
        return True     #Needed because returning None is the same as False which destroys the timer!


    def check_collision(self, car1_x, car1_y, car1_w, car1_h, car2_x, car2_y, car2_w, car2_h):
        #x - horizontal position
        #y - vertical position
        #w - width
        #h - height
        if(car1_x > RoadPositions.COLLISION_HORIZON or car2_x > RoadPositions.COLLISION_HORIZON): #If the cars have not yet appeared on screen then give them a chance of sorting it out
            return False
        return (car1_x < car2_x + car2_w) and (car1_x + car1_w > car2_x) and (car1_y < car2_y + car2_h) and (car1_y + car1_h > car2_y)

    def npv_collision(self, car1, car2):
        if(car1.vertical_position == car2.vertical_position):
            if(car1.horizontal_position <= car2.horizontal_position):
                car2.hit_from_behind()
            else:
                car1.hit_from_behind()
        else:
            if (not car1.crashed) and (not car2.crashed):
                ParticleManager.add_new_emmitter(SmokeEmitter(car1.horizontal_position, car1.vertical_position-car1.height_offset, -car1.speed, 0))
                car1.crashed = True
                car2.crashed = True
            car1.wobble()
            car2.wobble()

    def on_draw(self, wid, cr):
        #REMEMBER Order is important here
        self.road.draw(cr)
       
        for npv in self.npvs:
            npv.draw(cr)
       
        for item in self.droped_items:
            item.draw(cr)

        for player in self.players:
            player.draw(cr)

        ParticleManager.draw(cr)
        
        if self.paused:            
            cr.set_source_rgb(1, 1, 1)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            font_size=45
            cr.set_font_size(font_size)
            cr.move_to(Window.WIDTH/2-2.75*font_size, Window.HEIGHT/2)
            cr.show_text("PAUSED")
			

    def on_key_press(self, wid, event):
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == KeyboardKeys.KEY_ESC:
                self.paused = not self.paused
                self.darea.queue_draw()
            for i in range(len(self.players)):
                if event.keyval == KeyboardKeys.KEY_LEFT[i]: 
                    self.players[i].braking = True
                elif event.keyval == KeyboardKeys.KEY_RIGHT[i]:
                    self.players[i].forward = True
                elif event.keyval == KeyboardKeys.KEY_UP[i]: 
                    self.players[i].up = True
                elif event.keyval == KeyboardKeys.KEY_DOWN[i]:
                    self.players[i].down = True
                elif event.keyval >= KeyboardKeys.KEY_ONE[i] and event.keyval <= KeyboardKeys.KEY_FIVE[i]:
                    self.players[i].usePowerUp(event.keyval-KeyboardKeys.KEY_TO_NUM[i])

    def on_key_release(self, wid, event):
        if event.type == Gdk.EventType.KEY_RELEASE:
            for i in range(len(self.players)):
                if event.keyval == KeyboardKeys.KEY_LEFT[i]:
                    self.players[i].braking = False
                elif event.keyval == KeyboardKeys.KEY_RIGHT[i]:
                    self.players[i].forward = False
                elif event.keyval == KeyboardKeys.KEY_UP[i]: 
                    self.players[i].up = False
                elif event.keyval == KeyboardKeys.KEY_DOWN[i]:
                    self.players[i].down = False

game = Game()
Gtk.main()
