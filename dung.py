import random

# Status effect system
class StatusEffect:
    def __init__(self, name, duration, apply_effect, expire_effect=None):
        self.name = name
        self.duration = duration
        self.apply_effect = apply_effect  # Function applied each turn
        self.expire_effect = expire_effect  # Function when effect expires
    
    def tick(self, entity):
        if self.duration > 0:
            self.apply_effect(entity)
            self.duration -= 1
            if self.duration == 0 and self.expire_effect:
                self.expire_effect(entity)

# Entity class (Player and Enemy)
class Entity:
    def __init__(self, name, hp, attack, defense=0):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.status_effects = []
    
    def is_alive(self):
        return self.hp > 0
    
    def take_damage(self, amount):
        damage_taken = max(0, amount - self.defense)
        self.hp -= damage_taken
        if self.hp < 0:
            self.hp = 0
        print(f"{self.name} takes {damage_taken} damage (after defense). Current HP: {self.hp}/{self.max_hp}")
    
    def attack_target(self, target):
        damage = random.randint(1, self.attack)
        print(f"{self.name} attacks {target.name} for {damage} damage!")
        target.take_damage(damage)
    
    def add_status(self, status):
        print(f"{self.name} is now affected by {status.name} for {status.duration} turns!")
        self.status_effects.append(status)
    
    def process_status_effects(self):
        for status in self.status_effects[:]:
            status.tick(self)
            if status.duration <= 0:
                print(f"{self.name} is no longer affected by {status.name}.")
                self.status_effects.remove(status)
    
    def has_status(self, name):
        return any(s.name == name for s in self.status_effects)

# Player class with leveling and inventory
class Player(Entity):
    def __init__(self, name="Hero"):
        super().__init__(name, hp=30, attack=8)
        self.x = 0
        self.y = 0
        self.floor = 0
        self.inventory = []
        self.explored = set()
        self.level = 1
        self.xp = 0
        self.xp_to_next = 20
        self.weapon = None
        self.armor = None
        self.quest = None
    
    def move(self, direction, dungeon):
        dx, dy = 0, 0
        if direction == 'w':  # up
            dy = -1
        elif direction == 's':  # down
            dy = 1
        elif direction == 'd':  # right
            dx = 1
        elif direction == 'a':  # left
            dx = -1
        else:
            print("Invalid direction!")
            return
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        if dungeon.is_valid_position(new_x, new_y, self.floor):
            self.x = new_x
            self.y = new_y
            print(f"\nMoved to ({self.x}, {self.y}) on floor {self.floor}")
            self.explored.add((self.floor, self.x, self.y))
            dungeon.enter_room(self)
            # Check random events
            dungeon.random_event(self)
        else:
            print("You can't move in that direction!")
    
    def gain_xp(self, amount):
        self.xp += amount
        print(f"You gained {amount} XP! Total XP: {self.xp}/{self.xp_to_next}")
        while self.xp >= self.xp_to_next:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next
        self.xp_to_next = int(self.xp_to_next * 1.5)
        self.max_hp += 5
        self.hp = self.max_hp
        self.attack += 2
        self.defense += 1
        print(f"*** Level Up! You are now level {self.level}! ***")
        print(f"Stats increased! HP: {self.max_hp}, Attack: {self.attack}, Defense: {self.defense}")
    
    def add_item(self, item):
        self.inventory.append(item)
        print(f"You picked up: {item.name}")
    
    def use_item(self):
        if not self.inventory:
            print("Your inventory is empty!")
            return
        
        print("Inventory:")
        for i, item in enumerate(self.inventory, 1):
            print(f"{i}: {item.name} - {item.description}")
        
        choice = input("Choose item number to use (or 'q' to cancel): ")
        if choice.lower() == 'q':
            return
        
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(self.inventory):
                print("Invalid choice.")
                return
            item = self.inventory.pop(idx)
            item.use(self)
        except ValueError:
            print("Invalid input.")
    
    def show_status(self):
        print(f"{self.name} HP: {self.hp}/{self.max_hp} | Level: {self.level} | XP: {self.xp}/{self.xp_to_next} | Attack: {self.attack} | Defense: {self.defense}")
        if self.status_effects:
            effects = ", ".join([f"{s.name}({s.duration})" for s in self.status_effects])
            print(f"Status Effects: {effects}")
        else:
            print("Status Effects: None")
    
    def show_map(self, dungeon):
        print(f"\nDungeon Map - Floor {self.floor} (X=You, .=explored, #=unexplored, S=stairs)")
        for y in range(dungeon.height):
            row = ""
            for x in range(dungeon.width):
                pos = (self.floor, x, y)
                room = dungeon.get_room(self.floor, x, y)
                if (x, y) == (self.x, self.y):
                    row += "X "
                elif pos in self.explored:
                    if room.is_stairs_up or room.is_stairs_down:
                        row += "S "
                    else:
                        row += ". "
                else:
                    row += "# "
            print(row)
        print("")

# Items and their types
class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def use(self, player):
        pass

class HealingPotion(Item):
    def __init__(self, heal_amount=20):
        super().__init__("Healing Potion", f"Restores {heal_amount} HP.")
        self.heal_amount = heal_amount
    
    def use(self, player):
        healed = min(player.max_hp - player.hp, self.heal_amount)
        player.hp += healed
        print(f"You used a Healing Potion and restored {healed} HP!")

class Weapon(Item):
    def __init__(self, name, attack_bonus):
        super().__init__(name, f"Increases attack by {attack_bonus}.")
        self.attack_bonus = attack_bonus
    
    def use(self, player):
        if player.weapon:
            print(f"You replace your {player.weapon.name} with {self.name}.")
            player.attack -= player.weapon.attack_bonus
        else:
            print(f"You equip {self.name}.")
        player.weapon = self
        player.attack += self.attack_bonus

class Armor(Item):
    def __init__(self, name, defense_bonus):
        super().__init__(name, f"Increases defense by {defense_bonus}.")
        self.defense_bonus = defense_bonus
    
    def use(self, player):
        if player.armor:
            print(f"You replace your {player.armor.name} with {self.name}.")
            player.defense -= player.armor.defense_bonus
        else:
            print(f"You equip {self.name}.")
        player.armor = self
        player.defense += self.defense_bonus

class Key(Item):
    def __init__(self):
        super().__init__("Dungeon Key", "Opens locked rooms.")

# Enemy Types with XP reward
class Enemy(Entity):
    def __init__(self, name, hp, attack, defense=0, xp_reward=10):
        super().__init__(name, hp, attack, defense)
        self.xp_reward = xp_reward

# NPCs and quests
class NPC:
    def __init__(self, name, quest=None):
        self.name = name
        self.quest = quest
    
    def talk(self, player):
        print(f"{self.name}: Hello traveler!")
        if self.quest and not self.quest.completed:
            print(f"{self.name}: I have a quest for you - {self.quest.description}")
            if not player.quest:
                player.quest = self.quest
        elif self.quest and self.quest.completed:
            print(f"{self.name}: Thank you for completing the quest!")
        else:
            print(f"{self.name}: Safe travels!")

# Quest class
class Quest:
    def __init__(self, description, target_enemy_name, target_count):
        self.description = description
        self.target_enemy_name = target_enemy_name
        self.target_count = target_count
        self.progress = 0
        self.completed = False
    
    def record_kill(self, enemy_name):
        if enemy_name == self.target_enemy_name and not self.completed:
            self.progress += 1
            print(f"Quest progress: {self.progress}/{self.target_count} {self.target_enemy_name}s defeated.")
            if self.progress >= self.target_count:
                self.completed = True
                print("Quest completed!")

# Room with traps, puzzles, NPCs, items, enemies, and stairs
class Room:
    def __init__(self, description, enemy=None, item=None, trap=None, npc=None, stairs=None, locked=False):
        self.description = description
        self.enemy = enemy
        self.item = item
        self.trap = trap
        self.npc = npc
        self.is_stairs_up = (stairs == "up")
        self.is_stairs_down = (stairs == "down")
        self.locked = locked
        self.cleared = False
    
    def enter(self, player):
        if self.locked:
            if any(isinstance(i, Key) for i in player.inventory):
                print("You use a key to unlock the door.")
                player.inventory = [i for i in player.inventory if not isinstance(i, Key)]
                self.locked = False
            else:
                print("This room is locked. You need a key.")
                return
        
        print(self.description)
        
        if self.cleared:
            print("This room is cleared.")
            return
        
        if self.trap:
            print("There is a trap here!")
            if self.trap.active:
                choice = input("Attempt to disarm the trap? (y/n): ").lower()
                if choice == 'y':
                    if random.random() < 0.6:
                        print("You disarmed the trap successfully!")
                        self.trap.active = False
                    else:
                        print("You failed to disarm the trap and got hit!")
                        player.take_damage(self.trap.damage)
                else:
                    print("You avoid the trap carefully.")
            else:
                print("The trap has been disarmed.")
        
        if self.npc:
            self.npc.talk(player)
        
        if self.enemy and self.enemy.is_alive():
            print(f"You encounter a {self.enemy.name}!")
            self.fight(player)
            if not self.enemy.is_alive():
                player.gain_xp(self.enemy.xp_reward)
                self.enemy = None
                self.cleared = True
        
        if self.item:
            print(f"You found an item: {self.item.name}")
            player.add_item(self.item)
            self.item = None
            self.cleared = True
    
    def fight(self, player):
        enemy = self.enemy
        while player.is_alive() and enemy.is_alive():
            player.process_status_effects()
            if not player.is_alive():
                break
            print(f"\nYour HP: {player.hp}/{player.max_hp}")
            print(f"{enemy.name} HP: {enemy.hp}/{enemy.max_hp}")
            action = input("Attack (a) or Use Item (i)?: ").lower()
            if action == 'a':
                player.attack_target(enemy)
            elif action == 'i':
                player.use_item()
                continue
            else:
                print("Invalid action.")
                continue
            
            if enemy.is_alive():
                enemy.process_status_effects()
                if enemy.has_status("Stun"):
                    print(f"{enemy.name} is stunned and skips its turn!")
                else:
                    enemy.attack_target(player)
        
        if not player.is_alive():
            print("You died!")
            exit()

# Trap class
class Trap:
    def __init__(self, damage):
        self.damage = damage
        self.active = True

# Dungeon with multiple floors and procedural generation
class Dungeon:
    def __init__(self, floors=3, width=5, height=5):
        self.floors = floors
        self.width = width
        self.height = height
        self.rooms = {}  # (floor, x, y) => Room
        self.generate_dungeon()
    
    def generate_dungeon(self):
        for floor in range(self.floors):
            for x in range(self.width):
                for y in range(self.height):
                    # Generate random rooms with low chance of enemy/trap/item/npc
                    enemy = None
                    item = None
                    trap = None
                    npc = None
                    stairs = None
                    locked = False
                    
                    # Random enemy
                    if random.random() < 0.15:
                        enemy = Enemy("Goblin", hp=15, attack=5, xp_reward=10)
                    
                    # Random trap
                    if random.random() < 0.1:
                        trap = Trap(damage=5)
                    
                    # Random item
                    if random.random() < 0.1:
                        item = HealingPotion()
                    
                    # Random NPC
                    if random.random() < 0.05:
                        quest = Quest("Defeat 2 Goblins", "Goblin", 2)
                        npc = NPC("Old Man", quest)
                    
                    # Random locked room with key
                    if random.random() < 0.03:
                        locked = True
                        item = Key()
                    
                    room = Room(f"An empty room at ({x},{y}) floor {floor}.", enemy, item, trap, npc, locked=locked)
                    self.rooms[(floor, x, y)] = room
            
            # Place stairs - up on floor > 0, down except last floor
            if floor > 0:
                x_up, y_up = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
                self.rooms[(floor, x_up, y_up)].is_stairs_up = True
            
            if floor < self.floors - 1:
                x_down, y_down = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
                self.rooms[(floor, x_down, y_down)].is_stairs_down = True
    
    def is_valid_position(self, x, y, floor):
        return 0 <= x < self.width and 0 <= y < self.height and (floor, x, y) in self.rooms
    
    def get_room(self, floor, x, y):
        return self.rooms.get((floor, x, y), None)
    
    def enter_room(self, player):
        room = self.get_room(player.floor, player.x, player.y)
        if room:
            room.enter(player)
        else:
            print("This room doesn't exist.")
    
    def random_event(self, player):
        # 5% chance of random event per move
        if random.random() < 0.05:
            print("A wild rat appears!")
            rat = Enemy("Giant Rat", hp=10, attack=3, xp_reward=5)
            room = Room("An open area where a Giant Rat attacks!", enemy=rat)
            room.fight(player)
            if not rat.is_alive():
                player.gain_xp(rat.xp_reward)

# Game loop and input handling
def main():
    dungeon = Dungeon()
    player = Player()
    player.floor = 0
    # Start player in stairs up or (0,0)
    started = False
    for (f, x, y), room in dungeon.rooms.items():
        if f == 0 and room.is_stairs_up:
            player.x = x
            player.y = y
            started = True
            break
    if not started:
        player.x, player.y = 0, 0
    
    print("Welcome to the Roguelike Dungeon!")
    player.show_status()
    dungeon.enter_room(player)
    
    while player.is_alive():
        player.show_status()
        player.show_map(dungeon)
        command = input("Enter command (w/a/s/d to move, i for inventory, q to quit): ").lower()
        if command in ['w', 'a', 's', 'd']:
            player.move(command, dungeon)
            
            # Check stairs transitions
            current_room = dungeon.get_room(player.floor, player.x, player.y)
            if current_room.is_stairs_up:
                if player.floor > 0:
                    player.floor -= 1
                    print("You climb the stairs up one floor.")
                    # Move player to stairs down of new floor, if exists
                    for (f, x, y), room in dungeon.rooms.items():
                        if f == player.floor and room.is_stairs_down:
                            player.x, player.y = x, y
                            break
                    dungeon.enter_room(player)
            elif current_room.is_stairs_down:
                if player.floor < dungeon.floors - 1:
                    player.floor += 1
                    print("You descend the stairs down one floor.")
                    # Move player to stairs up of new floor, if exists
                    for (f, x, y), room in dungeon.rooms.items():
                        if f == player.floor and room.is_stairs_up:
                            player.x, player.y = x, y
                            break
                    dungeon.enter_room(player)
        
        elif command == 'i':
            player.use_item()
        elif command == 'q':
            print("Thanks for playing!")
            break
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
