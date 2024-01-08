
 * Required libraries

  - numpy
  - nashpy
  - matplotlib

 * Suggested interpreter

   - python 3.10

 * Use

From directory 'src', program is launched with "python3 main.py".

 - Fight menu: play a battle with (minimalist) graphical interface
 - Test menu: run several battles and report results

Parameters refer to the following:

 - player/agent(1/2): type of agent for player1/2 (in fight mode, player1 can be user)
   - "ga" option uses a neural network trained with evolutionary algorithm on 5 * 10 generations
   - "rl" option uses a neural network trained with gradient based algorithm on 10 * 10000 iterations
 - nb: number of battles for comparison
 - eps: set the epsilon value for epsilon-greedy
