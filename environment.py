from typing import Optional
import numpy as np
import gymnasium as gym
from gymnasium.spaces import OneOf, Box, Dict
import client
import cv2


class TankwarsEnv(gym.Env):

    def __init__(self, client):
        self.client = client
        self.observation_space = Box(0, 255, shape=(200, 200, 3), dtype=np.uint8)
        self.action_space = Dict({
            "right_engine": Box(-1, 1, shape=(1,), dtype=np.float32),
            "left_engine": Box(-1, 1, shape=(1,), dtype=np.float32),
            "fire": OneOf(True, False),
        })

        def get_state(self, player_id):
            self.client.request_observation(player_id, self.client.ObservationKind.IMAGE)
            return self.client.player_state(player_id)

        def get_info(self):
            pass

        def reset(self, seed=None):
            # super().reset(seed=seed)

            print("Requesting a player to be controlled")
            player_id = client.get_player()

            if player_id is None:
                return print("Failed to receive a player to control, quitting!")

            # 2. Subscribe to images and rewards for the spawned player
            print("Subscribing to player")
            client.subscribe_to_observation(player_id, self.client.ObservationKind.IMAGE, cooldown=0.1)
            client.subscribe_to_observation(player_id, self.client.ObservationKind.REWARDS, cooldown=0.1)

            return player_id

        def step(self, player_id, controls):
            self.client.send_controls(player_id, controls)
            player_state = self.get_state(player_id)
            reward = player_state.pop("reward", 0.0)
            terminated = False
            truncated = False
            info = self.get_info()

            return player_state, reward, terminated, truncated, info

        def render(self, player_id, player_state):
            image = player_state.get("image")
            if image is not None:
                cv2.imshow(f"Player #{player_id:160x}", image)
                cv2.waitKey(1)  # Refresh the window to update the image

            else:
                print("Player image was not set, skipping")

        gym.register(
            id="gymnasium_env/Tankwars-v0",
            entry_point=TankwarsEnv,
        )