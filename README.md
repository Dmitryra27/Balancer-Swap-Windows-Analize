# Balancer Swap Windows Idea Analize

This repository contains the files for analize of the Idea of reduction of the impermanent loss associated with a change in the composition of the pool. 
The Idea named Swap Windows is to open up the possibility of exchanging tokens in certain time intervals.

The situation is simulated when the user community decided to change the composition of the pool Tokens.
We open the opportunity of swaps and change the weights such way to arbitrageurs lead the pool to a new state.

In this study used three strategies for changing weights.
We try to find the Strategy with miminum losses.

Strategy 1 - weights change immediately.
Strategy 2 - weights change gradually over a given period.
Strategy 3 is an attempt to change weights when market prices move in the direction of the desired composition of Tokens and in the opposite direction.

A computational experiment was carried out.
The charts show the effectiveness of strategies.
