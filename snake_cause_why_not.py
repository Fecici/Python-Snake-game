import pygame, sys, random, time

WIDTH, HEIGHT = 1000, 800
RES = (WIDTH, HEIGHT)
FPS = 120
FPS_FACTOR = 13
TICK_STOP = FPS // FPS_FACTOR

TS = 25  # tilesize

ROW, COL = HEIGHT // TS, WIDTH // TS

class Colour:
    def __init__(self) -> None:
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.WHITE = (255, 255, 255)

colour = Colour()

class Snake:
    def __init__(self, game, x: int, y: int, length: int, direction: str) -> None:
        self.blocks = []
        self.game = game

        self.x, self.y = x, y
        self.length = length
        self.direction = direction
        self.previous_moved_direction = direction

        for i in range(self.length):
            self.blocks.append(pygame.Rect(self.x, self.y, TS, TS))

    def movement(self, keys):

        if (keys[pygame.K_w] or keys[pygame.K_UP]) and not (self.direction == 'd' or self.previous_moved_direction == 'd'):
            self.direction = 'u'

        if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and not (self.direction == 'u' or self.previous_moved_direction == 'u'):
            self.direction = 'd'

        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and not (self.direction == 'r' or self.previous_moved_direction == 'r'):
            self.direction = 'l'

        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and not (self.direction == 'l' or self.previous_moved_direction == 'l'):
            self.direction = 'r'

    def update(self):

        match self.direction:
            case 'r':
                self.x += TS
                if self.game.wall_hack:
                    if self.x + TS > WIDTH:
                        self.x = 0
                self.previous_moved_direction = 'r'

            case 'l':
                self.x -= TS
                if self.game.wall_hack:
                    if self.x < 0:
                        self.x = WIDTH - TS
                self.previous_moved_direction = 'l'

            case 'u':
                self.y -= TS
                if self.game.wall_hack:
                    if self.y < 0:
                        self.y = HEIGHT - TS
                self.previous_moved_direction = 'u'

            case 'd':
                self.y += TS
                if self.game.wall_hack:
                    if self.y + TS > HEIGHT:
                        self.y = 0
                self.previous_moved_direction = 'd'

            case _:
                raise ValueError('Fuck')
        
        new_head = pygame.Rect(self.x, self.y, TS, TS)
        
        self.blocks.append(new_head)

        for apple in self.game.apples:
            if new_head.colliderect(apple.get_rect()):

                self.game.apples.remove(apple)

                self.game.generate_apple()
                self.length += 1
                print('ate apple', end=' ')
                break  # stops the else, and should not conflict with any other apples because the apples dont generate ontop of each other

        else:
            print('else') 
            sx, sy = self.blocks[0].x // TS, self.blocks[0].y // TS
            self.game.grid[sy][sx] = 0
            self.blocks.pop(0)

        if not self.game.wall_hack:
            if (0 > self.x or WIDTH <= self.x) or (0 > self.y or HEIGHT <= self.y):

                print('out of bounds death')
                
                main()  # just restart the game on death
                
        self.game.grid[self.y // TS][self.x // TS] = 1  # set head to 1 in array

        if not (self.game.game_just_started or self.game.body_collision_hack):
            for block in self.blocks[:-1]:
                
                if new_head.x == block.x and new_head.y == block.y:  # could probably just use colliderect

                    print('snake collision death')
                    main()


    def draw(self):
        for rect in self.blocks:
            
            pygame.draw.rect(self.game.screen, colour.GREEN, rect)

class Apple:
    def __init__(self, game) -> None:
        self.game = game

        # if self.game.toggle_breakpoint_apple_grid:
        #     pass

        valid_coords = []
        for i, row in enumerate(self.game.grid):
            for j, col in enumerate(row):
                if col == 0:
                    valid_coords.append((j, i))


        self._do_draw = False
        if valid_coords:
            coords = random.choice(valid_coords)
            self._do_draw = True

        else:
            coords = -1000, -1000  # just toss away the apple to the void
        ax, ay = coords

        if valid_coords: self.game.grid[ay][ax] = 1

        self.x, self.y = ax * TS, ay * TS

        self.rect = pygame.Rect(self.x, self.y, TS, TS)

    def get_rect(self):
        return self.rect

    def draw(self):
        if self._do_draw: pygame.draw.rect(self.game.screen, colour.RED, self.rect)

    def run_away(self):
        up_dy = self.y - TS
        down_dy = self.y + TS
        left_dx = self.x - TS
        right_dx = self.x + TS

        xcoords = [left_dx, right_dx]
        ycoords = [up_dy, down_dy]

        
        if right_dx + TS > WIDTH:
            if self.game.wall_hack:
                right_dx = 0
            
            else:
                xcoords.remove(right_dx)

        if left_dx < 0:
            if self.game.wall_hack:
                left_dx = WIDTH - TS
            
            else:
                xcoords.remove(left_dx)

        if up_dy < 0:
            if self.game.wall_hack:
                up_dy = HEIGHT - TS
            
            else:
                ycoords.remove(up_dy)

        if down_dy + TS > HEIGHT:
            if self.game.wall_hack:
                down_dy = 0
            
            else:
                ycoords.remove(down_dy)

        if not (xcoords or ycoords):  # see if this even works
            return -1, -1
        # else:


class Game:
    def __init__(self) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((RES))
        pygame.display.set_caption('Snake lol')
        self.run = False
        self.FPS = FPS
        self.FPSClock = pygame.time.Clock()
        self.tick_rate = 0

        self.grid = []

        self.game_just_started = True

        for r in range(ROW):
            self.grid.append([0] * COL)

        # debug/cheats:
        self.wall_hack = False
        self.body_collision_hack = False
        self.toggle_breakpoint_apple_grid = False

        # delta time
        self.ti = 0

        # initialize snake and apple
        self.snake = Snake(self, COL // 2 * TS, ROW // 2 * TS, 13, 'r')
        self.apples = [Apple(self)]
        
    def mk_grid(self) -> None:
        for i in range(ROW):
            pygame.draw.line(self.screen, colour.WHITE, (0, i * TS), (WIDTH, i * TS))

        for j in range(COL):
            pygame.draw.line(self.screen, colour.WHITE, (j * TS, 0), (j * TS, HEIGHT))

        # end lines that are out of bounds, with fixed width
        pygame.draw.line(self.screen, colour.WHITE, (0, HEIGHT), (WIDTH, HEIGHT), width=4)
        pygame.draw.line(self.screen, colour.WHITE, (WIDTH, 0), (WIDTH, HEIGHT), width=4)

    def generate_apple(self):
        self.apples.append(Apple(self))

    def _spawn_apple(self):
        apple = Apple(self)

        self.apples.append(apple)

        return apple.x, apple.y

    def _debug_tools(self, keys):
        if keys[pygame.K_LSHIFT]:
            if keys[pygame.K_k]:
                self.wall_hack = not self.wall_hack
                print(f'WALL HACK: {self.wall_hack}')

            if keys[pygame.K_b]:
                self.body_collision_hack = not self.body_collision_hack
                print(f'BODY COLLISIONS HACK: {self.body_collision_hack}')

            if keys[pygame.K_n]:
                x, y = self._spawn_apple()
                print(f'Spawned a new apple at {(x, y)}')

        if keys[pygame.K_LCTRL]:
            if keys[pygame.K_o]:

                if self.FPS - 1 > 0: self.FPS -= 1
                print(f'FPS: {self.FPS}')

            if keys[pygame.K_p]:

                self.FPS += 1
                print(f'FPS: {self.FPS}')

        if keys[pygame.K_g]:
            for i in range(50):
                x, y = self._spawn_apple()
                print(f'Spawned a new apple at {(x, y)}')

        if keys[pygame.K_y]:
            self.toggle_breakpoint_apple_grid = not self.toggle_breakpoint_apple_grid

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                quit()

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                self.snake.movement(keys)
                self._debug_tools(keys)

    def update(self):
        self.screen.fill(colour.BLACK)

        self.snake.draw()

        for apple in self.apples:
            apple.draw()

        if self.tick_rate >= TICK_STOP:
            self.tick_rate = 0
            
            self.snake.update()
            self.game_just_started = False

        self.mk_grid()
        pygame.display.update()

    def start(self) -> None:

        self.run = True
        while self.run:
            self.tick_rate += 1
            self.FPSClock.tick(self.FPS)

            self.events()
            self.update()

def main() -> None:

    game = Game()
    game.start()

if __name__ == "__main__":
    main()