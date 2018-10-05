import time
import random

print('\n\n\n')

player_money = 0
player_switch_money = 0


doors = [1,2,3]
for i in range(1000):
	# select winning door and players door
	win_door = random.choice(doors)
	player_door = random.choice(doors)
	
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
		
	print('round:',i+1,'win:',win_door,'player:',player_door,'open:',open_door,'switch:',player_switch_door,'money:', player_money,' switch money:',player_switch_money)

	if i < 10:
		input('')
	else:
		time.sleep(0.01)
			
