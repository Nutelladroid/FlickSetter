import time
import random
import numpy as np
from numpy import random as rand
import configparser
import os

from rlbot.agents.base_script import BaseScript
from rlbot.utils.game_state_util import GameState, BallState, CarState, \
    Physics, Vector3, Rotator, GameInfoState
from rlbot.utils.structures.game_data_struct import GameTickPacket

DegToRad = 3.14159265 / 180


# game_state = GameState()

class FlickSetter(BaseScript):

    def __init__(self):
        super().__init__('Flick Setter')

    def start(self):

        rng = rand.default_rng()

        # Set up old score
        
        old_score = 0
        start_test = 0


        while 1:

            # when packet available

            packet = self.wait_game_tick_packet()

            # Checks if goal has been scored and setups up cars

            if not packet.game_info.is_round_active:
                continue
            #score if ball touches ground (sometimes doesn't work when ball is going too fast, but good enough)
            if packet.game_ball.physics.location.z < 97 and packet.game_ball.physics.location.y != 0:
                if start_test ==1:
                    ball_state = BallState(Physics(location=Vector3(0, -5500, 300)))
                    self.set_game_state(GameState(ball=ball_state))
                
                if start_test == 0:
                    start_test = 1
                  
                
            
            #If score changes, reset players and ball
            if packet.teams[0].score + packet.teams[1].score \
                != old_score or packet.game_ball.physics.location.y == 0:
                old_score = packet.teams[0].score \
                    + packet.teams[1].score

                car_states = {}

                for p in range(packet.num_cars):
                    car = packet.game_cars[p]

                    # Team 0 location (attacker) and ball placement

                    if car.team == 0:
                        desired_car_pos = Vector3(0.0, -4608, 17)

                        rand_x = int( rng.uniform(0, 3000))
                        rand_y = int(rng.uniform(-2000, 2000))
                        rand_z = 19
                        rand_x_vel = rng.uniform(0, 0)
                        rand_y_vel = rng.uniform(0, 1100)
                        desired_car_pos = Vector3(rand_x, rand_y, rand_z)  # x, y, z
                        desired_yaw = (90 + (rng.uniform(5, 15))) * DegToRad
                        desired_car_vel = [rand_x_vel, rand_y_vel , 0]
                        car_state = CarState(boost_amount=rand.uniform(40, 100),physics=Physics(location=desired_car_pos,rotation=Rotator(yaw=desired_yaw, pitch=0,roll=0), velocity=Vector3(rand_x_vel, rand_y_vel, 0),angular_velocity=Vector3(0, 0, 0)))
                        car_states[p] = car_state
                        # put ball on top of car, slight random perturbations
                        desired_ball_posx = rand_x + rng.uniform(-0, 0)
                        desired_ball_posy = rand_y + rng.uniform(0, 0) +  12
                        desired_ball_posz = 150 + rng.uniform(5, 20)
                        ball_state = BallState(Physics(location=Vector3(desired_ball_posx,desired_ball_posy,desired_ball_posz), velocity=Vector3(rand_x_vel, rand_y_vel, 0)))
						#Team 1 location (defender)
                    elif car.team == 1:
                        desired_car_pos = Vector3(rng.uniform(-1600, 1600),  rng.uniform(3800, 5000), 17)
                        car_state = CarState(boost_amount=rand.uniform(33,50),physics=Physics(location=desired_car_pos,rotation=Rotator(0, rng.uniform(-180, 180) * (np.pi / 180), 0),velocity=Vector3(rand_x_vel, rand_y_vel, 0),angular_velocity=Vector3(0, 0, 0)))
                        car_states[p] = car_state

               #sets the players and ball
                self.paused_car_states = car_states
                self.game_state = GameState(ball=ball_state,
                        cars=car_states)
                self.set_game_state(self.game_state)


if __name__ == '__main__':
    flick_setter = FlickSetter()
    flick_setter.start()
