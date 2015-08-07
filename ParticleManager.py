import cairo

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
    def __init__(self, x, y, speed_x, speed_y, size, shape, num_of_particles, rate):
        global __particlePool__
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.size = size
        self.shape = shape
        self.pool = __particlePool__
        self.particles = []
        self.particle_count = num_of_particles
        self.rate = rate
        self.done = False


    #Must be outside of constructor so that particles are only reserved after emitter is aproved
    def init_particles(self):
        self.particles = [self.pool.request_particle() for i in range(self.particle_count)]
        self.set_particles()

    #abstract
    def set_particles(self):
        pass

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
 

__particlePool__ = ParticlePool(Particles.POOLED_PARTICLES)
__particleEmitters__ = []

def add_new_emmitter(new_emmiter):
    global __particleEmitters__
    if len(__particleEmitters__) < Particles.MAX_EMMITTERS:
        __particleEmitters__.append(new_emmiter)
        new_emmiter.init_particles()

def update(time_delta):
    global __particleEmitters__
    for pe in __particleEmitters__[:]:
        pe.update(time_delta)
        if pe.isDone():
            __particleEmitters__.remove(pe)

def draw(cr):
    global __particleEmitters__
    for pe in __particleEmitters__:
        pe.draw(cr)
