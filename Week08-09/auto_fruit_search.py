# M4 - Autonomous fruit searching

# basic python packages
import sys, os
import cv2
import numpy as np
import json
import argparse
import time

# import SLAM components
# sys.path.insert(0, "{}/slam".format(os.getcwd()))
# from slam.ekf import EKF
# from slam.robot import Robot
# import slam.aruco_detector as aruco

# import utility functions
sys.path.insert(0, "util")
from pibot import PenguinPi
import measure as measure


def read_true_map(fname):
    """Read the ground truth map and output the pose of the ArUco markers and 3 types of target fruit to search

    @param fname: filename of the map
    @return:
        1) list of target fruits, e.g. ['apple', 'pear', 'lemon']
        2) locations of the target fruits, [[x1, y1], ..... [xn, yn]]
        3) locations of ArUco markers in order, i.e. pos[9, :] = position of the aruco10_0 marker
    """
    with open(fname, 'r') as fd:
        gt_dict = json.load(fd)
        fruit_list = []
        fruit_true_pos = []
        aruco_true_pos = np.empty([10, 2])

        # remove unique id of targets of the same type
        for key in gt_dict:
            x = np.round(gt_dict[key]['x'], 1)
            y = np.round(gt_dict[key]['y'], 1)

            if key.startswith('aruco'):
                if key.startswith('aruco10'):
                    aruco_true_pos[9][0] = x
                    aruco_true_pos[9][1] = y
                else:
                    marker_id = int(key[5])
                    aruco_true_pos[marker_id][0] = x
                    aruco_true_pos[marker_id][1] = y
            else:
                fruit_list.append(key[:-2])
                if len(fruit_true_pos) == 0:
                    fruit_true_pos = np.array([[x, y]])
                else:
                    fruit_true_pos = np.append(fruit_true_pos, [[x, y]], axis=0)

        return fruit_list, fruit_true_pos, aruco_true_pos


def read_search_list():
    """Read the search order of the target fruits

    @return: search order of the target fruits
    """
    search_list = []
    with open('search_list.txt', 'r') as fd:
        fruits = fd.readlines()

        for fruit in fruits:
            search_list.append(fruit.strip())

    return search_list


def print_target_fruits_pos(search_list, fruit_list, fruit_true_pos):
    """Print out the target fruits' pos in the search order

    @param search_list: search order of the fruits
    @param fruit_list: list of target fruits
    @param fruit_true_pos: positions of the target fruits
    """

    print("Search order:")
    n_fruit = 1
    for fruit in search_list:
        for i in range(3):
            if fruit == fruit_list[i]:
                print('{}) {} at [{}, {}]'.format(n_fruit,
                                                  fruit,
                                                  np.round(fruit_true_pos[i][0], 1),
                                                  np.round(fruit_true_pos[i][1], 1)))
        n_fruit += 1


# Waypoint navigation
# the robot automatically drives to a given [x,y] coordinate
# additional improvements:
# you may use different motion model parameters for robot driving on its own or driving while pushing a fruit
# try changing to a fully automatic delivery approach: develop a path-finding algorithm that produces the waypoints

def drive_to_point(waypoint, robot_pose):
    # imports camera / wheel calibration parameters
    fileS = "calibration/param/sim/scale.txt"
    scale = np.loadtxt(fileS, delimiter=',') # meters/tick
    fileB = "calibration/param/sim/baseline.txt"
    baseline = np.loadtxt(fileB, delimiter=',') # meters

    ####################################################
    # TODO: replace with your codes to make the robot drive to the waypoint
    # One simple strategy is to first turn on the spot facing the waypoint,
    # then drive straight to the way point

    waypoint_x = waypoint[0]
    waypoint_y = waypoint[1]
    robot_x = robot_pose[0]
    robot_y = robot_pose[1]
    robot_theta = robot_pose[2]
    waypoint_angle = np.arctan2((waypoint_y-robot_y),(waypoint_x-robot_x))

    angle = robot_theta - waypoint_angle

    distance = np.sqrt((waypoint_x-robot_x)**2 + (waypoint_y-robot_y)**2) #calculates distance between robot and object

    print(f'Turn {angle} and drive {distance}')

    wheel_vel = 30 #ticks
    # Convert to m/s
    left_speed_m = wheel_vel * scale
    right_speed_m = wheel_vel * scale

    # Compute the linear and angular velocity
    linear_velocity = (left_speed_m + right_speed_m) / 2.0

    # Convert to m/s
    left_speed_m = -wheel_vel * scale
    right_speed_m = wheel_vel * scale

    angular_velocity = (right_speed_m - left_speed_m) / baseline

    print(f'Ang vel is {angular_velocity}')
    # turn towards the waypoint
    turn_time = abs(angle/angular_velocity)

    print("Turning for {:.2f} seconds".format(turn_time))
    if angle >= 0:
        ppi.set_velocity([0, -1], turning_tick=wheel_vel, time=turn_time)
    else:
        ppi.set_velocity([0, 1], turning_tick=wheel_vel, time=turn_time)
    # after turning, drive straight to the waypoint
    drive_time = distance/linear_velocity
    print("Driving for {:.2f} seconds".format(drive_time))
    ppi.set_velocity([1, 0], tick=wheel_vel, time=drive_time)
    ####################################################

    print("Arrived at [{}, {}]".format(waypoint[0], waypoint[1]))

    new_robot_pose = [waypoint_x, waypoint_y, waypoint_angle]
    return new_robot_pose

def get_robot_pose():
    ####################################################
    # TODO: replace with your codes to estimate the pose of the robot
    # We STRONGLY RECOMMEND you to use your SLAM code from M2 here

    # update the robot pose [x,y,theta]
    robot_pose
    ####################################################

    return robot_pose

# main loop
if __name__ == "__main__":
    parser = argparse.ArgumentParser("Fruit searching")
    parser.add_argument("--map", type=str, default='M4_true_map.txt')
    parser.add_argument("--ip", metavar='', type=str, default='localhost')
    parser.add_argument("--port", metavar='', type=int, default=40000)
    args, _ = parser.parse_known_args()

    ppi = PenguinPi(args.ip,args.port)

    # read in the true map
    fruits_list, fruits_true_pos, aruco_true_pos = read_true_map(args.map)
    search_list = read_search_list()
    print_target_fruits_pos(search_list, fruits_list, fruits_true_pos)

    # waypoint = [0.0,0.0]
    # robot_pose = [0.0,0.0,0.0]

    # # The following code is only a skeleton code the semi-auto fruit searching task
    # while True:
    #     # enter the waypoints
    #     # instead of manually enter waypoints, you can get coordinates by clicking on a map, see camera_calibration.py
    #     x,y = 0.0,0.0
    #     x = input("X coordinate of the waypoint: ")
    #     try:
    #         x = float(x)
    #     except ValueError:
    #         print("Please enter a number.")
    #         continue
    #     y = input("Y coordinate of the waypoint: ")
    #     try:
    #         y = float(y)
    #     except ValueError:
    #         print("Please enter a number.")
    #         continue

    #     # estimate the robot's pose
    #     robot_pose = get_robot_pose()

    #     # robot drives to the waypoint
    #     waypoint = [x,y]
    #     drive_to_point(waypoint,robot_pose)
    #     print("Finished driving to waypoint: {}; New robot pose: {}".format(waypoint,robot_pose))

    #     # exit
    #     ppi.set_velocity([0, 0])
    #     uInput = input("Add a new waypoint? [Y/N]")
    #     if uInput == 'N':
    #         break


    from path_planning.RRT import *
    #Set parameters
    goal = np.array([1.25, 1.25]) + 1.5
    start = np.array([0, 0]) + 1.5

    # all_obstacles = read_obstacles

    obstacles = [[1,1],[-0.5,0.5],[1,-0.5]]
    for i in range(len(obstacles)):
        x, y = obstacles[i]
        obstacles[i] = [x + 1.5, y + 1.5]
    print(obstacles)
    all_obstacles = generate_path_obstacles(obstacles)

    rrtc = RRT(start=start, goal=goal, width=3, height=3, obstacle_list=all_obstacles,
            expand_dis=0.5, path_resolution=0.25)
    path = rrtc.planning()[::-1]

    img = cv2.imread("path_planning/grid.png")
    img = draw_obstacles(img, obstacles)
    img = draw_path(img, path)

    for i in range(len(path)):
        x, y = path[i]
        path[i] = [x - 1.5, y - 1.5]
    print(f'The path is {path}')

    cv2.imshow('image',img)
    cv2.waitKey(0)

    robot_pose = [0,0,0]
    for waypoint in path[1:]:
        print(f'Driving to waypoint {waypoint}')
        robot_pose = drive_to_point(waypoint, robot_pose)
        print(f'Finished driving to waypoint {waypoint}')



