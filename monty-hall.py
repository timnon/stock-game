import time
import random

print('\n\n\n')

player_money = 0
player_switch_money = 0

player_door_ix = input("select door: ")
player_door_ix = int(player_door_ix)
print('------------------------------------------------------------')

doors = [1,2,3]
for i in range(1000):
	# select winning door and players door
	win_door = random.choice(doors)
	player_door = doors[player_door_ix-1]

	# open door and select switch door
	open_door = random.choice([ door for door in doors if door not in {win_door,player_door} ])
	player_switch_door = [ door for door in doors if door not in {open_door,player_door} ][0]
	player_switch_money -= 200

	# player win
	if player_door == win_door:
		player_money += 1000

	# player wins with switching
	if player_switch_door == win_door:
		player_switch_money += 1000

	print(f'round: {i+1} | win door: {win_door} | {player_money}$ vs {player_switch_money}$ with switch')

	if i < 10:
		input('')
	else:
		time.sleep(0.01)
	time.sleep(0.0001)
