import time
import numpy as np 
import configparser 
from numpy import random as rand
import os
from threading import Timer

from rlbot.agents.base_script import BaseScript
from rlbot.utils.game_state_util import GameState, BallState, CarState, \
    Physics, Vector3, Rotator, GameInfoState
from rlbot.utils.structures.game_data_struct import GameTickPacket

deg_to_rad = 3.14159265 / 180


class FlickSetter(BaseScript):

    def __init__(self):
        super().__init__('Flick Setter')
        self.timer_set = False

    def get_bool_from_config(self, section, option):
        return True if self.config.get(section, option).lower() in {"true", "1"} else False

    def get_float_from_config(self, section, option):
        return float(self.config.get(section, option))

    def get_int_from_config(self, section, option):
        return int(self.get_float_from_config(section, option))


    def reset_timer(self,packet, config_time):
        #resets and sets main timer
        if hasattr(self, 'Timer'):
            self.Timer.cancel()
        self.Timer = Timer(config_time, self.defender_score, [packet])
        self.Timer.start()
        
    
    def defender_score(self,packet):
        
        ball_state = BallState(Physics(location=Vector3(0, -5500, 300)))
        self.set_game_state(GameState(ball=ball_state))
       
        

    def set_players(self,packet,orange_set,blue_set,hard_mode, min_initial_speed, max_initial_speed,config_time):
        self.timer_set = False
        car_states = {}
        #short hand for later use :)
        rng = rand.default_rng()
        
        #reset and set timer
        self.reset_timer(packet, config_time)


        for p in range(packet.num_cars):
            car = packet.game_cars[p]

            # Team 0 location (attacker) and ball placement

            if car.team == 0:
                desired_car_pos = Vector3(0.0, -4608, 17)

                if blue_set < 1:
                    blue_set =1
                    rand_x = int( rng.uniform(-3000, 3000))
                    rand_y = int(rng.uniform(-2000, 2000))
                    rand_z = 19
                    rand_x_vel = rng.uniform(-2, 2) + hard_mode * rng.uniform(-250, 250)
                    
                    #Sets initial speed of attacker, takes into account if hard mode is enabled and the user defined speeds
                    rand_y_vel = rng.uniform(min_initial_speed, max_initial_speed)
                    
                    if hard_mode > 0:
                         rand_y_vel = rng.uniform(500, 2000)
                    
                    desired_car_pos = Vector3(rand_x, rand_y, rand_z)
                    desired_yaw = (90 + (rng.uniform(-5, 5))) * deg_to_rad+ hard_mode * (rng.uniform(-10, 10)) * deg_to_rad
                    desired_car_vel = [rand_x_vel, rand_y_vel , 0]
                    car_state = CarState(boost_amount=rand.uniform(40, 100),physics=Physics(location=desired_car_pos,rotation=Rotator(yaw=desired_yaw, pitch=0,roll=0), velocity=Vector3(rand_x_vel, rand_y_vel, 0),angular_velocity=Vector3(0, 0, 0)))
                    car_states[p] = car_state
                    # put ball on top of car, slight random perturbations
                    if rand_x>0:
                        desired_ball_posx = rand_x + rng.uniform(-10 * hard_mode, 10)
                    else:
                        desired_ball_posx = rand_x + rng.uniform(-10, 10 * hard_mode)
                    
                    desired_ball_posy = rand_y  + 2 + hard_mode * rng.uniform(-7, 3)
                    desired_ball_posz = 150 + 12 + hard_mode * rng.uniform(-22, 7)
                    ball_state = BallState(Physics(location=Vector3(desired_ball_posx,desired_ball_posy,desired_ball_posz), velocity=Vector3(rand_x_vel, rand_y_vel, 0),angular_velocity=Vector3(hard_mode* rng.uniform(-2, 2),hard_mode* rng.uniform(-2, 2),hard_mode* rng.uniform(-2, 2))))
                elif blue_set > 0:
                    desired_car_pos = Vector3(0.0, -4608, 17)
                    car_state = CarState(boost_amount=rand.uniform(0, 0),physics=Physics(location=desired_car_pos,rotation=Rotator(yaw=desired_yaw, pitch=0,roll=0), velocity=Vector3(rand_x_vel, rand_y_vel, 0),angular_velocity=Vector3(0, 0, 0)))
                    car_states[p] = car_state
                #Team 1 location (defender)
            elif car.team == 1:
                if orange_set < 1:
                    orange_set =1
                    desired_car_pos = Vector3(rng.uniform(-1600, 1600),  rng.uniform(3800, 5000), 17)
                    car_state = CarState(boost_amount=rand.uniform(33,50),physics=Physics(location=desired_car_pos,rotation=Rotator(0, rng.uniform(-180, 180) * (np.pi / 180), 0),velocity=Vector3(rand_x_vel, rand_y_vel, 0),angular_velocity=Vector3(0, 0, 0)))
                    car_states[p] = car_state
                elif orange_set > 0:
                    desired_car_pos = Vector3(0.0, -4608, 17)
                    car_state = CarState(boost_amount=rand.uniform(0, 0),physics=Physics(location=desired_car_pos,rotation=Rotator(yaw=desired_yaw, pitch=0,roll=0), velocity=Vector3(rand_x_vel, rand_y_vel, 0),angular_velocity=Vector3(0, 0, 0)))
                    car_states[p] = car_state

       #sets the players and ball
        self.paused_car_states = car_states
        self.game_state = GameState(ball=ball_state,
                cars=car_states)
        self.set_game_state(self.game_state)
    
    def start(self):
    
        #Imports config settings
        self.config = configparser.ConfigParser()
        file_path =os.path.join(os.path.dirname(os.path.realpath(__file__)), "flicksetter.cfg")
        self.config.read(file_path, encoding="utf8")
        
        hard_setter_enabled = self.get_bool_from_config('Options', 'hard_setter_enabled')
        max_initial_speed = self.get_int_from_config('Options', 'max_initial_speed')
        min_initial_speed = self.get_int_from_config('Options', 'min_initial_speed')
        config_time = self.get_int_from_config('Options', 'time_reset')
        bounce_delay = self.get_int_from_config('Options', 'bounce_delay')
        
        #It later multiplies hard mode values to 0 if not enabled
        if hard_setter_enabled == True:
            hard_mode = 1
        else:
            hard_mode = 0
        
        #Making sure that user didn't put silly values in the config
        if max_initial_speed > 2000 :
            max_initial_speed = 2000
        
        if min_initial_speed < 0 :
            min_initial_speed
        
        if min_initial_speed > max_initial_speed :
            max_initial_speed = min_initial_speed
        
        
        

        # Set up old score
        
        old_score = 0
        start_test = 0
        orange_set = 0
        blue_set = 0


        while 1:

            # when packet available

            packet = self.wait_game_tick_packet()

            # Checks if goal has been scored and setups up cars

            if not packet.game_info.is_round_active:
                continue
            #score if ball touches ground (sometimes doesn't work when ball is going too fast, but good enough)
            if packet.game_ball.physics.location.z < 97 and packet.game_ball.physics.location.y != 0:
                if start_test ==1:
                    
                    if self.timer_set == False:
                        if bounce_delay > 0:
                            self.reset_timer(packet, bounce_delay)
                            self.timer_set = True
                        else:
                            self.defender_score(packet)

                
                if start_test == 0:
                    start_test = 1
                  
                
            
            #If score changes, reset players and ball
            if packet.teams[0].score + packet.teams[1].score \
                != old_score or packet.game_ball.physics.location.y == 0:
                old_score = packet.teams[0].score \
                    + packet.teams[1].score

                self.set_players(packet,orange_set,blue_set,hard_mode,min_initial_speed, max_initial_speed,config_time)


if __name__ == '__main__':
    flick_setter = FlickSetter()
    flick_setter.start()
