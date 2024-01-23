#!/usr/bin/env python3
# -*- coding: utf-8 -*-

########################################################################################################################
# Authors: Marcel Breyer, Alexander Van Craen                                                                          #
# Copyright (C): 2024 Alexander Van Craen, Marcel Breyer, and Dirk Pflüger                                             #
# License: This file is released under the MIT license. See the LICENSE file in the project root for full information. #
########################################################################################################################

import argparse
from dataclasses import dataclass
from dataclass_csv import DataclassWriter
import math
import random

# parse command line arguments
parser = argparse.ArgumentParser(prog="generate_data", description="Generate a data set consisting of two galaxies "
                                                                   "colliding with each other.")

parser.add_argument("-o", "--output",
                    help="the output filename containing the Cartesian State Vectors in CSV format",
                    required=True)
parser.add_argument("-n", "--num_particles",
                    help="the number of particles in the data set",
                    type=int,
                    required=True)
parser.add_argument("-r", "--ratio",
                    help="the ratio of particles between the large and small galaxy (0.0 = all particles are located "
                         "in the large galaxy)",
                    type=float,
                    default=0.2)

args = parser.parse_args()

# calculate G using the correct units
gravitational_constant_si = 6.67440e-11  # m^3 / (kg * s^2)
solar_mass_in_kg = 1.988435e30           # kg
parsec_in_m = 3.08567758129e16           # m
year_in_s = 365.25 * 86400.0             # s
G = (solar_mass_in_kg * year_in_s * (gravitational_constant_si / parsec_in_m) *
     (1.0 / parsec_in_m) * (1.0 / parsec_in_m) * year_in_s)


# a class representing a single particle
@dataclass
class Body:
    id: int
    mass: float
    pos_x: float
    pos_y: float
    pos_z: float
    vel_x: float
    vel_y: float
    vel_z: float


# calculate the velocity of current_p such that it orbits black_hole
def set_orbital_velocity(current_p, black_hole):
    # calculate distance to black hole in parsec
    x = black_hole.pos_x - current_p.pos_x
    y = black_hole.pos_y - current_p.pos_y
    z = black_hole.pos_z - current_p.pos_z
    dist = math.sqrt(x * x + y * y + z * z)

    # based on the distance from the black hole calculate the velocity needed to maintain a circular orbit
    v = math.sqrt(G * black_hole.mass / dist)

    # calculate a suitable vector perpendicular to r for the velocity of the tracer
    current_p.vel_x = (y / dist) * v
    current_p.vel_y = (-x / dist) * v
    current_p.vel_z = (z / dist) * v * 0.1


# the resulting list containing all particles
particles = []
# the number of particles orbiting the big black holw
num_particles_big_black_hole = int(args.num_particles * (1.0 - args.ratio))

# create the particles
for i in range(args.num_particles):
    p = Body(i, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    if i == 0:
        # big black hole
        p.mass = 1000000.0
    elif i < num_particles_big_black_hole:
        # all bodies orbiting the big black hole
        r = 0.1 + 0.8 * (20.0 * random.random())
        a = 2.0 * math.pi * random.random()

        p.mass = 0.03 + 20.0 * random.random()
        p.pos_x = r * math.sin(a)
        p.pos_y = r * math.cos(a)
        p.pos_z = ((random.randint(0, 1) * 2 - 1) *
                   min(1.5 / math.sqrt(p.pos_x * p.pos_x + p.pos_y * p.pos_y) * 2.0, 1.5) * random.random() +
                   0.8 * random.random())

        set_orbital_velocity(p, particles[0])
    elif i == num_particles_big_black_hole:
        # small black hole
        p.mass = 100000.0
        p.pos_x = 20.0
        p.pos_y = 20.0

        set_orbital_velocity(p, particles[0])
        p.vel_x *= 0.9
        p.vel_y *= 0.9
        p.vel_z *= 0.9
    else:
        # all bodies orbiting the small black hole
        r = 0.1 + 0.8 * (6.0 * random.random())
        a = 2.0 * math.pi * random.random()

        p.mass = 0.03 + 20.0 * random.random()
        p.pos_x = r * math.sin(a)
        p.pos_y = r * math.cos(a)
        p.pos_z = ((random.randint(0, 1) * 2 - 1) *
                   min(1.0 / math.sqrt(p.pos_x * p.pos_x + p.pos_y * p.pos_y), 1.0) * random.random()
                   + 0.2 * random.random())
        p.pos_x += particles[num_particles_big_black_hole].pos_x
        p.pos_y += particles[num_particles_big_black_hole].pos_y

        set_orbital_velocity(p, particles[num_particles_big_black_hole])
        p.vel_x += particles[num_particles_big_black_hole].vel_x
        p.vel_y += particles[num_particles_big_black_hole].vel_y
        p.vel_z += particles[num_particles_big_black_hole].vel_z

    particles.append(p)


# write all particles to a CSV file
with open(args.output, 'w+') as csvfile:
    w = DataclassWriter(csvfile, particles, Body)
    w.write()
