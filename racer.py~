from gi.repository import Gtk, Gdk, GLib
import cairo
import random
import math

# 1 meter = 36 pixels !!

class Window:
    WIDTH = 1024
    HEIGHT = 512
    SCORE_POS_X = 50
    SCORE_POS_Y = 50
    VERSION = "v1.5"

class KeyboardKeys:
    KEY_LEFT  = 65361
    KEY_RIGHT = 65363
    KEY_UP = 65362
    KEY_DOWN = 65364

class RoadPositions:
    UPPER_LIMIT = 135
    LOWER_LIMIT = 375
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

class SkidMarks:
    SKID_LEFT = cairo.ImageSurface.create_from_png("skid_left.png")
    SKID_RIGHT= cairo.ImageSurface.create_from_png("skid_right.png")

class Particles:
    SMOKE = cairo.ImageSurface.create_from_png("./smoke_particle.png")
    FIRE = cairo.ImageSurface.create_from_png("./fire.png")
    POINTS = cairo.ImageSurface.create_from_png("./points.png")
    PLUS_100_POINTS = cairo.ImageSurface.create_from_png("./plus100points.png")
    MINUS_100_POINTS = cairo.ImageSurface.create_from_png("./minus100points.png")
    MAX_EMMITTERS = 10 
    POOLED_PARTICLES = 200
    WIDTH = 64
    HEIGHT = 64

class CarModels:
    GALLARDO = cairo.ImageSurface.create_from_png("gallardo.png")
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

    AVAILABLE_CARS = ( CORVETTE, CHARGER, GOLF, INTEGRA, SUPRA, F430, CCX, DB9, F1, SUPERLEGGERA, GT, LP570, MURCIELAGO, R8, RS4, SL65, SLR )
    EMERGENCY_CARS = ( AMBULANCE, COP )

class Particle:
    def __init__(self, x=0, y=0, life=0, angle=0, speed_x=0, speed_y=0, size=0, shape=None, deflate=True):
        self.set_properties(x, y, life, angle, speed_x, speed_y, size, shape, deflate)

    def set_properties(self, x, y, life, angle, speed_x, speed_y, size, shape, deflate):
        self.x = x
        self.y = y
        self.life = life
        self.original_life = life
        self.angle = angle
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = size
        self.original_size = size
        self.shape = shape
        self.alpha = 1
        self.deflate = deflate

    def update(self, time_delta):
        self.life -= time_delta
        if self.life > 0:
            age_ratio = float(self.life) / float(self.original_life)
            if self.deflate:
                self.size = self.original_size * age_ratio if age_ratio > 0.5 else self.size
            else:
                self.size = self.original_size / age_ratio if age_ratio > 0.5 else self.size
            self.alpha = age_ratio

            self.x += self.speed_x * time_delta
            self.y += self.speed_y * time_delta

    def draw(self, cr):
        cr.save()
        cr.translate(self.x, self.y)
        cr.scale(self.size/Particles.WIDTH , self.size/ Particles.HEIGHT)
        cr.set_source_surface(self.shape, 0, 0)
        cr.paint_with_alpha(self.alpha)
        cr.restore()

class ParticlePool:
    def __init__(self, pool_size):
        self.pool_size = pool_size
        self.pool = [ Particle() for i in range(pool_size) ] 
        self.ready_particle_count = pool_size

    def request_particle(self):
        if self.ready_particle_count == 0:
            print("Available particles limit EXCEEDED!!!")
            return None
        particle = self.pool[self.ready_particle_count-1]
        self.ready_particle_count -= 1
        return particle

    def return_particle(self, returning_particle):
        moved_particle = self.pool[self.ready_particle_count]
        position_to_move_into = self.pool.index(returning_particle)
        self.pool[self.ready_particle_count] = returning_particle
        self.pool[position_to_move_into] = moved_particle
        self.ready_particle_count += 1

class ParticleEmitter:
    def __init__(self, pool, num_of_particles, rate):
        self.pool = pool
        self.particle_count = num_of_particles
        self.particles = [self.pool.request_particle() for i in range(num_of_particles)]
        self.rate = rate
        self.done = False

    def update(self, time_delta):
        live_particles_count = 0
        new_emissions = self.rate*time_delta
        newly_emitted = 0
        for particle in self.particles:
            if particle.life > 0 and particle.life < particle.original_life:
                live_particles_count += 1
                particle.update(time_delta)
            elif particle.life > 0 and newly_emitted < new_emissions:
                live_particles_count += 1
                particle.update(time_delta)
                newly_emitted += 1

        if live_particles_count == 0:
            for particle in self.particles:
                self.pool.return_particle(particle)
            self.done = True

    def isDone(self):
        return self.done

    def draw(self, cr):
        if self.done:
            return
        for particle in self.particles:
            if particle.life > 0:
                particle.draw(cr)
 

class SmokeEmitter(ParticleEmitter):
    def __init__(self, pool, x, y, speed_x, speed_y):
        super(SmokeEmitter, self).__init__(pool, 20, 0.1)
        for particle in self.particles:
            particle.set_properties(x, y, 500, math.pi/2, speed_x + random.randrange(-5, 5)*Speed.ONE_KMH, speed_y + random.randrange(-5, 5)*Speed.ONE_KMH,  25, Particles.SMOKE, False)

class PointsEmitter(ParticleEmitter):
    def __init__(self, pool, x, y, speed_x, speed_y, size=100, shape=Particles.POINTS):
        super(PointsEmitter, self).__init__(pool, 1, 1)
        for particle in self.particles:
            particle.set_properties(x, y, 700, 0, speed_x + random.randrange(-5, 5)*Speed.ONE_KMH, speed_y + random.randrange(-5, 5)*Speed.ONE_KMH,  size, shape, True)

class Plus100Points(PointsEmitter):
    def __init__(self, pool):
        super(Plus100Points, self).__init__(pool, 50, 130, Speed.MAX_KMH*Speed.ONE_KMH, 0.1, 200, Particles.PLUS_100_POINTS)

class Minus100Points(PointsEmitter):
    def __init__(self, pool):
        super(Minus100Points, self).__init__(pool, 50, 130, Speed.MAX_KMH*Speed.ONE_KMH, 0.1, 400, Particles.MINUS_100_POINTS)

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
    def __init__(self, model, x, y, speed):
        super(Player, self).__init__(model, x, y, speed)
        self.draw_rotation = False
        self.up = False
        self.down = False
        self.forward = False
        self.braking = False
        self.crashHandler = None
        self.score = 0
        self.score_hundreds = 0

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
        box_x = self.horizontal_position; #begining of the car
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
            if (other_car.horizontal_position - self.horizontal_position) < 170:
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

class PlayerCrashHandler:
    ACCELARATION = 0.000005
    def __init__(self, player):
        self.t = 0
        self.player = player
        self.player.speed -= (10*Speed.ONE_KMH) if (player.speed >= Speed.MAX_KMH*Speed.ONE_KMH) else player.speed
        if (random.randrange(2) == 0) and player.vertical_position > RoadPositions.UPPER_LIMIT+20: 
            jolt = -20 
        elif player.vertical_position < RoadPositions.LOWER_LIMIT-20:
            jolt = 20
        else:
            jolt = -20
        self.player.vertical_position += jolt
        self.player.draw_rotation = True
        self.skid_mark = SkidMarks.SKID_LEFT if jolt < 0 else SkidMarks.SKID_RIGHT
        self.skid_marks_x = None
        self.skid_marks_y = None
        self.timeout = 1700
        #self.timeout = (self.player.speed)*(Window.WIDTH + self.player.width) Why doesnt this work??!?

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
            self.skid_marks_x += time_delta*(-self.player.speed) 

        self.t += time_delta
        if self.t >= self.timeout and self.player.draw_rotation == False:
            self.player.crash_handler = None

    def draw(self, cr):
        cr.save()
        cr.translate(self.skid_marks_x, self.skid_marks_y - self.player.height_offset)
        cr.set_source_surface(self.skid_mark, 0, 0)
        cr.paint()
        cr.restore()


class Game(Gtk.Window):

    def __init__(self):
        super(Game, self).__init__()
        self.init_ui()
        self.road = Road(0)
        self.vertical_position = RoadPositions.MIDDLE_LANE
        self.horizontal_position = 0
        self.rotation = 0
        self.draw_rotation = False
        self.width = cairo.ImageSurface.get_width(CarModels.GALLARDO)
        self.height = cairo.ImageSurface.get_height(CarModels.GALLARDO)
        self.height_offset = self.height/2
        self.up = False
        self.down = False
        self.forward = False
        self.braking = False
        self.speed = Speed.MAX_KMH*Speed.ONE_KMH
        self.add_tick_callback(self.update)
        self.last_update_timestamp = -1
        self.npvs = []
        self.spawn_delay = 0
        self.crash_handler = None
        self.score = 0
        self.score_hundreds = 0
        self.particlePool = ParticlePool(Particles.POOLED_PARTICLES)
        self.particleEmitters = []

    def init_ui(self):
        self.darea = Gtk.DrawingArea()
        self.darea.connect("draw", self.on_draw)
        self.add(self.darea)
        self.set_title("GENERIC RACER!!! " + Window.VERSION)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.resize(Window.WIDTH, Window.HEIGHT)
        self.set_size_request(Window.WIDTH, Window.HEIGHT)
        self.connect("delete-event", Gtk.main_quit)
        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        self.add_events(Gdk.EventMask.KEY_RELEASE_MASK)
        self.connect("key-press-event", self.on_key_press)
        self.connect("key-release-event", self.on_key_release)
        self.show_all()
        self.set_resizable(False)
    
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
        speed = self.speed - Speed.ONE_KMH*(random.randrange(20) + 5) # -5 beacause we need the npvs to always be slower than the player

        #Select a car
        random_num = random.randrange(100)
        if random_num > 4:
            return NPV(CarModels.AVAILABLE_CARS[random.randrange(len(CarModels.AVAILABLE_CARS))], lane, speed)
        else:
            return NPV(CarModels.EMERGENCY_CARS[random.randrange(len(CarModels.EMERGENCY_CARS))], lane, -20*Speed.ONE_KMH)

    def update(self, wid, fc):
        current_time = fc.get_frame_time()
        if self.last_update_timestamp == -1:
            self.last_update_timestamp = current_time
        time_delta = (current_time - self.last_update_timestamp)/1000 # frame time is in microseconds, we want miliseconds




        for i in range(self.score_hundreds - int(self.score / 100)):
            if len(self.particleEmitters) < Particles.MAX_EMMITTERS:
                self.particleEmitters.append(Minus100Points(self.particlePool))
        self.score += 0.03 * time_delta
        old_score_hundreds = self.score_hundreds
        self.score_hundreds = int(self.score / 100)
        for i in range(self.score_hundreds-old_score_hundreds):
            if len(self.particleEmitters) < Particles.MAX_EMMITTERS:
                self.particleEmitters.append(Plus100Points(self.particlePool))

        self.road.advance(time_delta*self.speed)

        #Adjust postition to user input
        if self.up and self.vertical_position > RoadPositions.UPPER_LIMIT:
            self.vertical_position -= 5
        elif self.down and self.vertical_position < RoadPositions.LOWER_LIMIT:
            self.vertical_position += 5
        
        if self.forward and self.horizontal_position < RoadPositions.FORWARD_LIMIT:
            self.horizontal_position += 5
        elif self.braking and self.horizontal_position > RoadPositions.REAR_LIMIT:
            self.horizontal_position -= 5

        
        
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
                self.npvs.append(self.generateRandomNPV())
                self.spawn_delay = 900
        #Recalculate their position
        for npv in self.npvs:
            npv.check_overtake_need(self.npvs)
            npv.update(time_delta, self.speed)


        #Collision detection
        #(between player and non-players)
        for npv in self.npvs:
            if self.check_collision(self.horizontal_position, self.vertical_position, self.width, self.height, npv.horizontal_position, npv.vertical_position, npv.width, npv.height):
                npv.wobble()
                if len(self.particleEmitters) < Particles.MAX_EMMITTERS:
                    self.particleEmitters.append(SmokeEmitter(self.particlePool, npv.horizontal_position, npv.vertical_position-npv.height_offset, -npv.speed, 0))
                    self.particleEmitters.append(PointsEmitter(self.particlePool, self.horizontal_position, self.vertical_position, -self.speed, 0.2))
                self.score -= 10
                if(self.crash_handler == None):
                    self.crash_handler = PlayerCrashHandler(self)

        #(between non-players themselves)
        for i in range(len(self.npvs) - 1):
            for j in range(i+1, len(self.npvs)):
                if self.check_collision(self.npvs[i].horizontal_position, self.npvs[i].vertical_position, self.npvs[i].width, self.npvs[i].height, self.npvs[j].horizontal_position, self.npvs[j].vertical_position, self.npvs[j].width, self.npvs[j].height):
                    self.npv_collision(self.npvs[i], self.npvs[j])

        if self.crash_handler != None:
            self.crash_handler.update(time_delta)


        #Update Particle Emitters
        for pe in self.particleEmitters[:]:
            pe.update(time_delta)
            if pe.isDone():
                self.particleEmitters.remove(pe)

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
            if len(self.particleEmitters) < 5:
                self.particleEmitters.append(SmokeEmitter(self.particlePool, car1.horizontal_position, car1.vertical_position-car1.height_offset, -car1.speed, 0))
            car1.wobble()
            car2.wobble()

    def on_draw(self, wid, cr):
        #REMEMBER Order is important here
        self.road.draw(cr)
       
        if self.crash_handler != None:
            self.crash_handler.draw(cr)
       
        for npv in self.npvs:
            npv.draw(cr);
        
        
        cr.save()
        cr.translate(self.horizontal_position, self.vertical_position - self.height_offset);
        if self.draw_rotation:
            x = self.width/2.0
            y = self.height/2.0
            cr.translate(x, y)
            cr.rotate(self.rotation);
            cr.translate(-x,-y) 
        cr.set_source_surface(CarModels.GALLARDO, 0, 0)
        cr.paint()
        cr.restore()


        for pe in self.particleEmitters:
            pe.draw(cr)

        if(self.score > 0):
            cr.set_source_rgb(1, 1, 1)
        else:
            cr.set_source_rgb(1, 0, 0)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(20)
        cr.move_to(Window.SCORE_POS_X, Window.SCORE_POS_Y)
        cr.show_text("SCORE: " + str(int(self.score)))

    def on_key_press(self, wid, event):
        if event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == KeyboardKeys.KEY_LEFT: 
                self.braking = True
            elif event.keyval == KeyboardKeys.KEY_RIGHT:
                self.forward = True
            elif event.keyval == KeyboardKeys.KEY_UP: 
                self.up = True
            elif event.keyval == KeyboardKeys.KEY_DOWN:
                self.down = True
            elif event.keyval == 115:
                pass#self.particleEmitters.append(FireEmitter(self.particlePool, self.horizontal_position, self.vertical_position-self.height_offset, -self.speed, 0))
    
    def on_key_release(self, wid, event):
        if event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == KeyboardKeys.KEY_LEFT:
                self.braking = False
            elif event.keyval == KeyboardKeys.KEY_RIGHT:
                self.forward = False
            elif event.keyval == KeyboardKeys.KEY_UP: 
                self.up = False
            elif event.keyval == KeyboardKeys.KEY_DOWN:
                self.down = False

app = Game()
Gtk.main()
