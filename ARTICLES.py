import dash_core_components as dcc
import dash_html_components as html
import HELPER

def getArticlesList(lang_index=0):
	articles_list=[]
	for name in ARTICLES_DICT:
		index=ARTICLES_DICT[name][0]
		articles_list.append(
			html.Div(children=[
				dcc.Link( HELPER.tr(name), href=f'/articles/{index}' ),
			],
			className="w3-bar-item w3-button w3-mobile"
			)
		)
		articles_list.append(html.Br())
	return articles_list

def getArticleByNumber(index,lang_index=0):
	index_int=int(index)
	for name in ARTICLES_DICT:
		if index_int == ARTICLES_DICT[name][0]:
			return ARTICLES_DICT[name][1](lang_index)
	return invalidArticle()

def KnownIssues(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
		Updated 07/01/20
		
		Here's the current issues that exist or did exist in SPPD today:
		
		Bugs:
		
			* Red Wifi 200 Error - When your energy does not match.
			* The same unit keeps spawning when you have enough energy.
			* Double Jesus
			* Dark Angel Red target stays alive.
			* Disappearing units
			* Opponent's unit appears to die, but keeps re-appearing and doing damage.
			* Rubber Banding Units
			* Multiple Charges in a row off of a single charged unit.
			* If Dark Angel Red kills a mind-controled unit, that unit comes back at level 2 if it is not in your deck.
		
		Exploits - Which no one has been caught using:
		
			* Playing unplayable cards in PVE
				* https://youtu.be/dBr9F1iRQqs
			* Invincible Units in Challenge Mode
			* Cards at whatever level you want (Currently 3 Routes Still Remain)
			
		Exploits in development:
			
			* MBP Coop - Bypassing encryption of datastream.
				* https://www.youtube.com/watch?v=EcSuUKhInj8&t=38m27s
		
		Exploits Fixed:
		
			* June '20 - App Pausing - invincible units that still deal damage and rubberband.
			* June '20 - MBP or Mosquito Coop
				* https://youtu.be/ru9tvrlrMjU?t=838
				* The data stream that needed to be modified is now encrypted.
				* Includes Invicible Units
			* May '20 - Modifying skill point search radius or your own rank
				* Search Radius is now server-side.
			* March '20 - Modify NK Level
			* Ongoing - Modify Card Levels
				* Several past routes have been patched
				* Example: Hydeen's Toolbox
				
		Bugs Fixed:
			* June '20 - Changing your team's name
			* Too many to list.
	''',lang_index))

def ElvesAliensChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
Here's the Challenge Decks I used.

![Challenge Deck](https://i.imgur.com/eREL5CA.png)

* Kyle of the Drow Elves Speed multiplied by 1.8
* Elven King Bradley Speed multiplied by 1.8
* Blood Elf Bebe Speed multiplied by 1.8

* Alien Clyde Character Health/Damage multiplied by 1.3
* Alien Queen Red Character Health/Damage multiplied by 1.3
* Visitors Character Health/Damage multiplied by 1.3
* Alien Drone Character Health/Damage multiplied by 1.3
* Gizmo Ike Character Health/Damage multiplied by 1.3

Only had time for two 12-win runs, including one run in the top 1000 ranked players. Will do my 3rd run later.

The deck I chose (fan/sci) only matched maybe 1 or 2 opponents, but performed extremely well. I wouldn't change a single card.

I did lose to a Santa/SOMM/Sharon deck because the opponent had an amazing rotation and my hands were bad.

Reason to NOT pick other cards:

* KOTDE - too expensive, rushes to opponents side.
* Catapult Timmy - too slow, he would pair well with bradley but I don't have a place for him in my deck.
* 4AM - too expensive, you want to cycle to your space pilot bradley + blood elf bebe
* AQR - too expensive, warcry at base L3 is still garbage.
* Alien Drone - Health/Attack buff does nothing when they move so slow. Waste of 4 energy.
* Elven King Bradley - He's almost playable this challenge, but he gets swept by space pilot bradley.
* Gizmo Ike - Health/Attack buff makes no noticeable difference. Don't feed the opponent's Blood Elf Bebe. Also, too expensive.

Strategies with this deck:

  * With a 2.9 average cost, this deck is all about cycle to your strongest cards.
  * Don't play all your range units together, and even then space them out.
  * Don't even bother playing around Alien Clyde, just let him target whoever.
  * Try to bait opponent's Poison on just Space Pilot Bradley or just Visitors.
  * DSR + LBJ on opponent's Witch Garrison + Blood Elf Bebe (and less important - Visitors) is huge.
  * Protect the Blood Elf Bebe! - She's poisoned/almost dead? Drop Paladin in front and she'll get massive value while shielded.
  * Blood Elf Bebe can sneak a bar if you drop her midline on an empty field when opponent only needs 1 more hit to take their bar.
  * Good luck.

See the full Challenge Meta Report, including card/theme usage here:

[https://sppdreplay.net/challenge/5](https://sppdreplay.net/challenge/5)
	''',lang_index))
	
def DarkAngelChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Decks I used.
		
		* Sheriff Cartman cost increased by -1
		* Big Mesquite Murph cost increased by -1
		* Grand Wizard Cartman cost increased by -1
		* Mr. Slave Executioner cost increased by -1
		* Mimsy cost increased by -1
		* Officer Barbrady cost increased by -1
		* Santa Claus cost increased by -1
		* PC Principal cost increased by -1
		* Zen Cartman cost increased by -1
		* Priest Maxi cost increased by -1
		* A.W.E.S.O.M.-O 4000 cost increased by -1
		* The Coon cost increased by -1
		* Manbearpig cost increased by -1
		* Manbearpig Character Health/Damage multiplied by 1.3
		* Dark Mage Craig Character Health/Damage multiplied by 1.3
		* Witch Garrison Character Health/Damage multiplied by 1.3
		* Witch Doctor Token Character Health/Damage multiplied by 1.3
		* Imp Tweek Character Health/Damage multiplied by 1.3
		* Satan Character Health/Damage multiplied by 1.3
		* Sorceress Liane Character Health/Damage multiplied by 1.3
		* Dark Angel Red Character Health/Damage multiplied by 1.3
		
		12-x over 3 runs, including one run at 8k.
		
		The deck I chose (fan/mys) was the tier 1 meta deck.
		New Space Pilot Bradley has potential, I did lose 1 game against such deck, but it was easy enough for me to take down.
		
		Other decent cards this challenge:
		* LBJ
		* Grand Wizard Cartman (because he costs 5, DAR can bring him back)
		
		Strategies with this deck:
		
		  * Against Bradley decks, try to bring Bradley to your side.
		     * Play very wide, and have all your range units out.
			 * You can also swap Ninjew for Satan.
			 * Maxi to counter poison
		  * Best opening play was Staff into Zen Cartman into Catapult Timmy.
		  * DAR on Slave/Maxi/Ninjew are all good plays.
		  * Use DSR on ideally 3 of your opponent's 4+ cost units.
		  * Good luck.
		
		![Challenge Deck](https://i.imgur.com/rPpM88Q.png)
	
		See the full Challenge Meta Report, including card/theme usage here:
		
		[https://sppdreplay.net/challenge/1]
	''',lang_index))
	
def WhimpyKidChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Decks I used.
		
			* New Kid is Level 1 (including health and blast damage)
			* New Kid has no zap
		
		12-0 on my first runs, 9-3 on my last run around 7k.
		
		The deck I chose (fan/sci) was the tier 1 meta deck.
		New Space Pilot Bradley broke the meta same as old Elven King Bradley.
		
		I used Towelie instead of Witch Garrison in my last run, Witch Garrison is the better choice.
		Catapult Timmy is in a higher tier when paired with Bradley because he spawns two rats (assassins) that will freeze opponents in range.
		NK has no zap. You must defend even if the opponent's unit only has a sliver of health.
		
		Other great cards this challenge:
		* Superheros. Super Craig, General Disarray, Superfart
		* Blood Elf Bebe
		* Warboy Tweek
		* Rat Swarm
		* Dwarf Engineer Dougie with Bradley on-board.
		
		Strategies with this deck:
		
		  * Bradley is MVP, easily surives two Level 1 New Kid blasts.
		  * It's very cycle dependent. I'd generally lose a bar and come back to take all 3 bars within the first 2 minutes.
		  * Catapult's charge is GREAT when Bradley is on-board.
		  * Poison opponent's Bradley right away (hard to get more value than that because most are playing around poison).
		  * It's ok to waste your units to cycle to hand into Bradley + Assassins while bringing opponent to your side.
		  * If you don't get value off Bradley + Catapult + Assassins combo, you will lose.
		  * Good luck.
		
		![Challenge Deck](https://i.imgur.com/wA8TJWw.png)
	
		Total Decks: 24, MMR Avg: 6170, MMR Standard Deviation: 1035.6
		
		Percent | Themes
		------------ | -------------
		38% | fan,sci
		21% | sci,sup
		17% | adv,sci
		12% | mys,sci
		4% | mys,sup
		4% | fan,sup
		4% | adv,sup

		Percent | Cards
		------------ | -------------
		67% | Space Warrior Token
		57% | Warboy Tweek
		54% | Terrance and Phillip
		46% | Visitors
		38% | Space Pilot Bradley
		38% | Mind Control
		33% | Underpants Gnomes
		33% | Paladin Butters
		28% | Professor Chaos
		28% | Princess Kenny
		28% | Poison
		28% | Enforcer Jimmy
		25% | Super Fart
		25% | Super Craig
		25% | Powerfist Dougie
		25% | Bounty Hunter Kyle
		25% | Astronaut Butters
		21% | Witch Garrison
		21% | Toolshed
		21% | Rat Swarm
		21% | Mosquito
		21% | Mimsy
		21% | Doctor Timothy
		21% | Cyborg Kenny
		21% | Blood Elf Bebe
		17% | Le Bard Jimmy
		17% | Inuit Kenny
		17% | Chiorboy Butters
		17% | Catapult Timmy
		12% | Towelie
		12% | Robo Bebe
		12% | Mysterion
		12% | Lightning Bolt
		12% | Four-Assed Monkey
		12% | Fireball
		12% | Dwarf Engineer Dougie
		12% | Dogpoo
		12% | Bandita Sally
		8% | Zen Cartman
		8% | Stan of Many Moons
		8% | Smuggler Ike
		8% | Regeneration
		8% | Purify
		8% | Program Stan
		8% | Pigeon Gang
		8% | PC Principal
		8% | Nathan
		8% | Mecha Timmy
		8% | Human Kite
		8% | Hookhand Clyde
		8% | Hermes Kenny
		8% | General Disarray
		8% | Captain Diabetes
		8% | Arrowstorm
		8% | Alien Drone
		4% | Unholy Combustion
		4% | Tupperware
		4% | The Coon
		4% | The Amazingly Randy
		4% | Storyteller Jimmy
		4% | Sorceress Liane
		4% | Sizzler Stuart
		4% | Sharpshooter Shelly
		4% | Sexy Nun Randy
		4% | President Garrison
		4% | Marine Craig
		4% | Marcus
		4% | Hyperdrive
		4% | Hercules Clyde
		4% | Hallelujah
		4% | Friar Jimmy
		4% | Freeze Ray
		4% | Energy Staff
		4% | Elven King Bradley
		4% | Dwarf King Clyde
		4% | Cupid Cartman
		4% | Chomper
		4% | Calamity Heidi
		4% | Big Gay Al
		4% | Angel Wendy
	''',lang_index))

def SpacePilotsChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Decks I used.
		
			* Space Pilot Bradley is level 2
		
		These cards have 30% more health and 80% speed boost:
		
			* Powerfist Dougie
			* Astronaut Butters
			* Gizmo Ike
			* Cyborg Kenny
			* Four-Assed Monkey
		
		12-0 on my first 2 runs, 8-3 on my last run. I got redlynx. You know when your opponent drops dougie right before they died and you could have killed him, but you don't, then 5 seconds later you're dead and it turns out you lose the game? Yeah...
		Lag wins games, because SPPD was never designed to handle cards running at 4x-8x speed If your opponent drops a boosted assassin (or double-boost with bradley) mid-line, you will never be able to respond in time.
		Dougie will take a bar with his triple-shots or freeze your cards on his 2nd hit.
		Characters will die then come to life.
		You will kill an enemy unit while you still have your bar, then lose your bar a full second or two later.
		
		I specifically didn't include TNP because I want to cycle to Bradley and buffed assassins as fast as possible.
		
		The deck I chose (fan/sci) was the tier 1 meta deck, but tier 2 (not as strong) was (adv/sci).
		This deck looks so stupid, but it steamrolls everything.
		
		Strategies with this deck:
		
		  * Bradley is MVP
		  * Your big hitters are 4AM, Astro butters, and Gizmo Ike.
		  * Open with an assassin to throw it away or combo it with 2 assassins.
		  * Strongest opener was Astro -> 4AM -> Bradley behind your NK: 8x speed boost on 4AM, game will lag, but you should kill opponents units and take a bar.
		  * Bradley is great when you can freeze your opponents cards on your side (or their side with gizmo ike)
		  * Bradley survives a NK blast when he's at full health, so try to keep him alive.
		  * LBJ + 4AM deathwish is a great combo.
		  * LBJ doesn't kill boosted units, but he still gets good value.
		  * MC opponent's Bradley at full health and take a bar.
		  * MC opponent's Cyborg Kenny.
		  * MC opponent's 4AM if he has Bradley on the field and Bradley is out of reach.
		  * Freeze opponent's Dougie with Bradley + Assassin (and they lose 4 energy with nothing to show)
		  * Save Gnomes for Cyborg Kenny, or to trigger 4AM's deathwish on an empty board.
		
		![Challenge Deck](https://i.imgur.com/srR01wi.png)
	
		Total Decks: 35, MMR Avg: 6102, MMR Standard Deviation: 836.4
		
		Percent | Themes
		------------ | -------------
		37% | fan,sci
		23% | adv,sci
		20% | mys,sci
		17% | sci,sup
		3% | sci,neu

		Percent | Cards
		------------ | -------------
		91% | Cyborg Kenny
		89% | Space Pilot Bradley
		86% | Astronaut Butters
		74% | Four-Assed Monkey
		66% | Gizmo Ike
		60% | Powerfist Dougie
		54% | Mind Control
		49% | Visitors
		31% | Terrance and Phillip
		31% | Space Warrior Token
		31% | Rat Swarm
		23% | Underpants Gnomes
		20% | Warboy Tweek
		20% | Poison
		20% | Arrowstorm
		20% | A.W.E.S.O.M.-O 4000
		17% | Robo Bebe
		17% | Paladin Butters
		17% | Bounty Hunter Kyle
		14% | Witch Garrison
		14% | Mecha Timmy
		14% | Inuit Kenny
		14% | Dogpoo
		14% | Catapult Timmy
		11% | Super Fart
		11% | Super Craig
		11% | Mr. Hankey
		11% | Lightning Bolt
		11% | Alien Drone
		9% | Towelie
		9% | The Amazingly Randy
		9% | Sexy Nun Randy
		9% | Rogue Token
		9% | Program Stan
		9% | Professor Chaos
		9% | Princess Kenny
		9% | Priest Maxi
		9% | Le Bard Jimmy
		9% | Human Kite
		9% | Doctor Timothy
		9% | Canadian Knight Ike
		9% | Blood Elf Bebe
		6% | Zen Cartman
		6% | Tupperware
		6% | Toolshed
		6% | Regeneration
		6% | Pigeon Gang
		6% | Mr. Slave Executioner
		6% | Mosquito
		6% | Lava!
		6% | Kyle of the Drow Elves
		6% | Energy Staff
		6% | Dwarf Engineer Dougie
		6% | Dragonslayer Red
		6% | Bandita Sally
		3% | Unholy Combustion
		3% | The Master Ninjew
		3% | Swashbuckler Red
		3% | Stan the Great
		3% | Sharpshooter Shelly
		3% | Robin Tweek
		3% | Purify
		3% | Pope Timmy
		3% | PC Principal
		3% | Nathan
		3% | Mysterion
		3% | Medusa Bebe
		3% | Hookhand Clyde
		3% | Hercules Clyde
		3% | General Disarray
		3% | Freeze Ray
		3% | Enforcer Jimmy
		3% | Deckhand Butters
		3% | Cock Magic
		3% | Classi
		3% | Chiorboy Butters
		3% | Buccaneer Bebe
		3% | Alien Queen Red
		3% | Alien Clyde
	''',lang_index))
	
def CandyDestroyerChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Decks I used.
		* Captain Diabetes Health Attack +30%
		These cards cost 1 less:
		
			* Gunslinger Kyle
			* Mr. Mackey
			* Bounty Hunter Kyle
			* Robin Tweek
			* Mr. Hankey
			* Santa Claus
			* The Master Ninjew
			* Mint-Berry Crunch
		
		Mostly 12-x, with a few failed runs. My attempts around 6k were not with meta decks, but I still managed 12 wins. At 7k I managed 12-1.
		The only tough opponents had the POWER CORE: Hankey, Santa, Capt Diabetes, Mint-Berry Cruch.
		The deck I chose (adv/sup) counters the meta (sci/sup).
		This is a high skill ceiling deck, and if you don't have the right card rotation and your opponent does, you lose.
		
		Other strong meta cards were:
		
			* SOMM (most opponents were not running removal)
			* Robin Tweek into Capt Diabetes + Hankey/Santa and that's game over.
		
		Strategies with this deck:
		
		  * Sometimes LB on Capt Diabetes is the best play. He is VERY STRONG this week.
		  * FB leaves Capt Diabetes with a sliver of health, kill him ASAP
		  * If opponent LB, bait it out with Doctor Timothy, so you can get that SOMM charge off.
		  * If you can open with Santa, followed SOMM... and wait until SOMM charge is ready by itself. You can get a double SOMM charge off, and sci/sup can't do anything.
		  * MBC on Capt Diabetes every time, ideally with Santa on-board, followed by Hankey.
		  * Body block your SOMM so he doesn't get near mid-line. Either so he doesn't take damage or for your opponent to use MC.
		
		![Challenge Deck](https://i.imgur.com/ffitWBz.png)
	
		Total Decks: 51, MMR Avg: 6269, MMR Standard Deviation: 561.0
		
		Percent | Themes
		------------ | -------------
		39% | sci,sup
		24% | adv,sup
		14% | fan,sup
		10% | adv,sci
		6% | mys,sup
		4% | mys,sci
		4% | fan,mys

		Percent | Cards
		------------ | -------------
		75% | Captain Diabetes
		69% | Mr. Hankey
		65% | Santa Claus
		63% | Mint-Berry Crunch
		56% | Doctor Timothy
		47% | Bounty Hunter Kyle
		45% | Super Craig
		41% | Space Warrior Token
		39% | Mr. Mackey
		39% | Mosquito
		33% | Professor Chaos
		31% | Visitors
		28% | Terrance and Phillip
		27% | Enforcer Jimmy
		24% | Warboy Tweek
		24% | Poison
		20% | Super Fart
		20% | Stan of Many Moons
		18% | Gunslinger Kyle
		18% | General Disarray
		16% | Robin Tweek
		16% | Medicine Woman Sharon
		16% | Lightning Bolt
		16% | Human Kite
		14% | Blood Elf Bebe
		12% | Underpants Gnomes
		12% | The Master Ninjew
		12% | Mysterion
		12% | Arrowstorm
		10% | Toolshed
		10% | Rat Swarm
		10% | Program Stan
		10% | Paladin Butters
		10% | Fireball
		8% | Tupperware
		8% | Robo Bebe
		8% | Pigeon Gang
		8% | Mecha Timmy
		8% | Deckhand Butters
		6% | Towelie
		6% | ThunderBird
		6% | Sheriff Cartman
		6% | Inuit Kenny
		6% | Hookhand Clyde
		6% | Hermes Kenny
		6% | Dogpoo
		6% | Calamity Heidi
		6% | Bandita Sally
		6% | Angel Wendy
		4% | Zen Cartman
		4% | The Coon
		4% | The Amazingly Randy
		4% | Terrance Mephesto
		4% | Swordsman Garrison
		4% | Storyteller Jimmy
		4% | Regeneration
		4% | Princess Kenny
		4% | Priest Maxi
		4% | Powerfist Dougie
		4% | Power Bind
		4% | Pope Timmy
		4% | Pocahontas Randy
		4% | PC Principal
		4% | Outlaw Tweek
		4% | Nathan
		4% | Mind Control
		4% | Marine Craig
		4% | Lava!
		4% | Fastpass
		4% | Cyborg Kenny
		4% | Chiorboy Butters
		4% | Canadian Knight Ike
		4% | Barrel Dougie
		2% | Witch Garrison 1
		2% | Transmogrify 1
		2% | Smuggler Ike 1
		2% | Sixth Element Randy 1
		2% | Sexy Nun Randy 1
		2% | Satan 1
		2% | Rogue Token 1
		2% | Poseidon Stan 1
		2% | Pirate Ship Timmy 1
		2% | Mr. Slave Executioner 1
		2% | Mimsy 1
		2% | Marcus 1
		2% | Manbearpig 1
		2% | Le Bard Jimmy 1
		2% | Jesus 1
		2% | Gizmo Ike 1
		2% | Friar Jimmy 1
		2% | Energy Staff 1
		2% | Dwarf King Clyde 1
		2% | Dwarf Engineer Dougie 1
		2% | Chomper 1
		2% | Captain Wendy 1
		2% | Call Girl 1
		2% | Big Gay Al 1
		2% | Astronaut Butters 1
		2% | Alien Drone 1
		2% | Alien Clyde 1
	''',lang_index))
	
def SpeedChaserKyleChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Decks I used. Kyle's cost 1 less and get double speed.
		
		12-x three times, with a few failed runs. Managed 12-0 at 7k. Experimented with several decks. Lost a handful of times to players with better decks, until I settled on this one. Sometimes I'd lose two bars without having taken any. But I didn't struggle coming back to grab all 3 with this deck.
		It took a while to get the hang of. It's a complex deck.
		I brutally crushed a handful of opponents so bad, they gave up after the first bar.
		This deck is easy mode compared to Mys-Sci.
		
		Strategies with this deck:
		  * You can also swap chaos for superfart, but I liked him.
		  * Open with Mysterion
		  * Save Dougie Disarray for Doctor/Mecha Timmy.
		  * Save poison for kyle + another range unit
		  * This deck is an ebb-and-flow like the ocean. Play super slow until you are ready to push for a bar.
		  * If opponent's bar is almost gone, you can sneak it with either kyle faster than any headhunter.
		  * Good luck.
		
		![Challenge Deck](https://i.imgur.com/KKY2kz4.png)
	
		Total Decks: 52, MMR Avg: 6468, MMR Standard Deviation: 749.3
		
		Percent | Themes
		------------ | -------------
		23% | mys,sci
		19% | sci,sup
		19% | fan,sci
		10% | adv,sci
		8% | mys,sup
		6% | fan,mys
		6% | adv,sup
		6% | adv,mys
		2% | fan,sup
		2% | adv,fan

		Percent | Cards
		------------ | -------------
		69% | Bounty Hunter Kyle
		52% | Space Warrior Token
		48% | Terrance and Phillip
		46% | Visitors
		37% | The Master Ninjew
		35% | Warboy Tweek
		33% | Human Kite
		28% | Professor Chaos
		27% | Enforcer Jimmy
		25% | Poison
		23% | Super Fart
		23% | Super Craig
		23% | Kyle of the Drow Elves
		23% | Doctor Timothy
		23% | Chiorboy Butters
		21% | Mosquito
		21% | Hermes Kenny
		21% | Dogpoo
		19% | Mind Control
		19% | Cyborg Kenny
		17% | Unholy Combustion
		17% | Le Bard Jimmy
		17% | Gunslinger Kyle
		15% | Underpants Gnomes
		15% | Toolshed
		15% | Program Stan
		15% | Pope Timmy
		15% | Paladin Butters
		15% | General Disarray
		15% | Blood Elf Bebe
		13% | Towelie
		12% | Mysterion
		12% | Medusa Bebe
		12% | Medicine Woman Sharon
		12% | Inuit Kenny
		12% | Hookhand Clyde
		10% | Zen Cartman
		10% | Witch Garrison
		10% | Transmogrify
		10% | Robo Bebe
		10% | Rat Swarm
		10% | Priest Maxi
		10% | Energy Staff
		10% | Catapult Timmy
		8% | Powerfist Dougie
		8% | Pocahontas Randy
		8% | Mr. Slave Executioner
		8% | Mr. Hankey
		8% | Mecha Timmy
		8% | Dwarf Engineer Dougie
		8% | Chomper
		8% | Astronaut Butters
		8% | Arrowstorm
		6% | Tupperware
		6% | Swordsman Garrison
		6% | Sheriff Cartman
		6% | Sharpshooter Shelly
		6% | Sexy Nun Randy
		6% | Santa Claus
		6% | Nathan
		6% | Lightning Bolt
		6% | Hyperdrive
		6% | Hercules Clyde
		6% | Gizmo Ike
		6% | Dragonslayer Red
		6% | Deckhand Butters
		6% | Chicken Coop
		6% | Bandita Sally
		6% | Alien Drone
		4% | ThunderBird
		4% | The Coon
		4% | Starvin' Marvin
		4% | Stan the Great
		4% | Shieldmaiden Wendy
		4% | Robin Tweek
		4% | Regeneration
		4% | Power Bind
		4% | PC Principal
		4% | Mr. Mackey
		4% | Mimsy
		4% | Hallelujah
		4% | Friar Jimmy
		4% | Dwarf King Clyde
		4% | Calamity Heidi
		4% | Big Gay Al
		4% | Barrel Dougie
		4% | A.W.E.S.O.M.-O 4000
		2% | Witch Doctor Token 1
		2% | The Amazingly Randy 1
		2% | Stan of Many Moons 1
		2% | Smuggler Ike 1
		2% | Rogue Token 1
		2% | Purify 1
		2% | Princess Kenny 1
		2% | Pigeon Gang 1
		2% | Mint-Berry Crunch 1
		2% | Marine Craig 1
		2% | Manbearpig 1
		2% | Jesus 1
		2% | Ice Sniper Wendy 1
		2% | Freeze Ray 1
		2% | Four-Assed Monkey 1
		2% | Cupid Cartman 1
		2% | Captain Diabetes 1
		2% | Canadian Knight Ike 1
		2% | Call Girl 1
		2% | Buccaneer Bebe 1
		2% | Big Mesquite Murph 1
		2% | Alien Queen Red 1
		2% | Alien Clyde 1
	''',lang_index))
	
def FurryBeastsChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Decks I used. Furry Beasts get double health.
		
		12-x three times, though just barely. Managed 12-2 at 7k. Lost a few times to some seriously good players.
		
		Strategies with this deck:
		  * It may seem like a dumb pope->MBP deck, but it's a high skill deck, no doubt.
		  * ...Because if you don't cycle your cards in the right order, you're going to have a bad time.
		  * It's too hard to give more complex strategies, so here's the basic ones.
		  * Save Transmog/UC for MBP. Maybe Transmog Sorceress Liane.
		  * YPC before MBP OR before you pope -> MBP
		  * Always use Powerbind the instant City Wok Guy spawns. His first charge is ready in ~2 seconds, he gets insane value.
		  * LBJ for pigeons, maybe rats+other assassins.
		  * It's almost not worth it to Pope MBP if your opponent is just going to UC him.
		  * Try to get as much value out of hermes/staff whenever possible.
		  * DSR/Witch Garrison/4AM get a lot of value in this challenge meta. Watch out.
		  * My opponents laughed and farted when their pigeons took the first bar, but I was never worried - play it slow and have a gameplan.
		  * Lastly, I managed to pull off some next-level strats like I'm playing 4D chess - Paladin Butters -> shields MBP, then opponent UC's him - completely wasting 5 energy. I miraculously pulled that off 3 times during my runs, and it helps me win games I probably shouldn't have.
		    * If you think you can pull it off, spawn MBP several seconds before Paladin Butters dies, when you think your opponent has UC in his hand.
		
		![Challenge Deck](https://i.imgur.com/YAS03Hs.png)
	
		Total Decks: 37, MMR Avg: 6303, MMR Standard Deviation: 690.8
		Note: Had a few games where I forgot to record the cards the opponent played.
		
		Percent | Themes
		------------ | -------------
		41% | fan,mys
		35% | fan,sci
		5% | sci,sup
		5% | mys,sci
		5% | adv,mys
		3% | fan,sup
		3% | adv,sci
		3% | adv,fan

		Percent | Cards
		------------ | -------------
		73% | Rat Swarm
		59% | Pigeon Gang
		51% | The Amazingly Randy
		51% | Manbearpig
		49% | Unholy Combustion
		46% | City Wok Guy
		43% | Chicken Coop
		43% | Blood Elf Bebe
		41% | Pope Timmy
		32% | Transmogrify
		32% | Terrance and Phillip
		27% | Mr. Slave Executioner
		27% | Le Bard Jimmy
		27% | Energy Staff
		24% | Hermes Kenny
		22% | Warboy Tweek
		22% | Visitors
		22% | Poison
		22% | Paladin Butters
		22% | Four-Assed Monkey
		22% | Bounty Hunter Kyle
		19% | Towelie
		19% | Dragonslayer Red
		19% | Catapult Timmy
		16% | Witch Garrison
		16% | Power Bind
		14% | Zen Cartman
		14% | Underpants Gnomes
		14% | Space Warrior Token
		14% | Program Stan
		14% | Cyborg Kenny
		11% | Youth Pastor Craig
		11% | Sorceress Liane
		11% | Rogue Token
		11% | Elven King Bradley
		11% | Dogpoo
		11% | Chiorboy Butters
		8% | The Master Ninjew
		8% | Stan of Many Moons
		8% | Professor Chaos
		8% | Mosquito
		8% | Mind Control
		8% | Medusa Bebe
		8% | Doctor Timothy
		8% | Big Gay Al
		8% | Astronaut Butters
		8% | Arrowstorm
		8% | Alien Drone
		5% | Super Craig
		5% | Stan the Great
		5% | Santa Claus
		5% | Princess Kenny
		5% | Powerfist Dougie
		5% | Mimsy
		5% | Mecha Timmy
		5% | Kyle of the Drow Elves
		5% | Inuit Kenny
		5% | Grand Wizard Cartman
		5% | General Disarray
		5% | Enforcer Jimmy
		5% | Dwarf Engineer Dougie
		5% | Canadian Knight Ike
		3% | Terrance Mephesto
		3% | Swordsman Garrison
		3% | Sizzler Stuart
		3% | Shieldmaiden Wendy
		3% | Robin Tweek
		3% | Regeneration
		3% | Prophet Dougie
		3% | Priest Maxi
		3% | Pocahontas Randy
		3% | Nathan
		3% | Mysterion
		3% | Mint-Berry Crunch
		3% | Marcus
		3% | Lightning Bolt
		3% | Imp Tweek
		3% | Ice Sniper Wendy
		3% | Hallelujah
		3% | Dwarf King Clyde
		3% | Calamity Heidi
		3% | Buccaneer Bebe
		3% | Alien Queen Red
	''',lang_index))
	
def UltraSpeedCrewChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Decks I used. Spells cost 1, YPC costs 10.
		
		12-1 three times. Only lost in the mirror matches when Mysterion either was at the bottom of my deck or he got transmog'd. 24 of the games, I had 1 card just below challenge level. For an ultra speed challenge, this is a slow push deck where you need to know when to go from 1 or 2 units to flooding the board with spam.
		
		* Mysterion early is great, even if your opponent has Transmog, keep playing him when you can, because games sometimes go to overtime.
		* It's a good idea to transmog Mysterion... unless your opponent has GWC/Maxi, but even then it's a decent play.
		* The best strategy was the deathball. Cycle your cards until you open with a normal-speed unit (Super Craig), then put a kyle behind him, and spam.
		* Wait for opponent's Superfart before you spam (Or have your units shielded before your opponent will play superfart).
		* Any range unit not boosted, dies too fast. Would not recommend.
		* In the mirror matches KOTDE was KEY. Takes out Human Kite/BHK.
		* Transmog on human kite is ok if your opponent is a potatoe.
		* Try to use your Le Bard Jimmy when opponent has BHK or Human Kite in play. Paired with superfart - kills BHK/Human Kite.
		* Paladin + Mysterion/PrincessKenny is huge value.
		* Save Superfart for the multiple assassin rush.
		* Save Gnomes for Cyborg Kenny
		Good luck!
		
		![Challenge Deck](https://i.imgur.com/B48K8RI.png)
	
		Total Decks: 39, MMR Avg: 6208, MMR Standard Deviation: 711.8
		
		Percent | Themes
		------------ | -------------
		36% | sci,sup
		26% | fan,sup
		13% | mys,sup
		8% | adv,sci
		5% | mys,sci
		5% | adv,sup
		3% | fan,sci
		3% | fan,mys
		3% | adv,fan

		Percent | Cards
		------------ | -------------
		79% | Toolshed
		72% | Mysterion
		64% | Human Kite
		59% | Super Fart
		46% | Cyborg Kenny
		44% | Bounty Hunter Kyle
		41% | Program Stan
		38% | The Coon
		33% | Super Craig
		33% | Mosquito
		31% | Professor Chaos
		28% | Terrance and Phillip
		28% | Stan the Great
		28% | Princess Kenny
		26% | A.W.E.S.O.M.-O 4000
		23% | Visitors
		23% | Underpants Gnomes
		23% | Mind Control
		21% | Hermes Kenny
		21% | Doctor Timothy
		21% | Blood Elf Bebe
		18% | Transmogrify
		18% | Paladin Butters
		15% | Zen Cartman
		15% | The Master Ninjew
		15% | Poseidon Stan
		13% | Warboy Tweek
		13% | Space Warrior Token
		13% | Medicine Woman Sharon
		10% | Tupperware
		10% | Towelie
		10% | Le Bard Jimmy
		8% | Sheriff Cartman
		8% | Rat Swarm
		8% | Lightning Bolt
		8% | Lava!
		8% | Kyle of the Drow Elves
		8% | Inuit Kenny
		8% | Grand Wizard Cartman
		8% | General Disarray
		8% | Fireball
		8% | Dogpoo
		8% | Chomper
		8% | Captain Diabetes
		8% | Call Girl
		8% | Astronaut Butters
		5% | Witch Garrison
		5% | Unholy Combustion
		5% | Stan of Many Moons
		5% | Sixth Element Randy
		5% | Sexy Nun Randy
		5% | Santa Claus
		5% | Regeneration
		5% | Pope Timmy
		5% | Poison
		5% | Mr. Hankey
		5% | Mecha Timmy
		5% | Hyperdrive
		5% | Hookhand Clyde
		5% | Hallelujah
		5% | Enforcer Jimmy
		5% | Cupid Cartman
		5% | Chiorboy Butters
		5% | Chicken Coop
		5% | Alien Drone
		3% | ThunderBird
		3% | The Amazingly Randy
		3% | Rogue Token
		3% | Robo Bebe
		3% | Priest Maxi
		3% | Power Bind
		3% | Pigeon Gang
		3% | Officer Barbrady
		3% | Nathan
		3% | Mimsy
		3% | Marine Craig
		3% | Hercules Clyde
		3% | Gunslinger Kyle
		3% | Gizmo Ike
		3% | Fastpass
		3% | Energy Staff
		3% | Dwarf King Clyde
		3% | Dwarf Engineer Dougie
		3% | Dragonslayer Red
		3% | Classi
		3% | Catapult Timmy
		3% | Bandita Sally
		3% | Arrowstorm
		3% | Angel Wendy
	''',lang_index))
	
def SpellbendersChallenge2(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Decks I used. Spells cost 1, YPC costs 10.
		
		12-0 twice, and 12-1 once using this deck. Lost to a funky Adv/Fan deck who played really well. This is an aggressive deck, and you can get 3-bars with it. The Adv/Fan decks are too slow. Either draw or 1 bar, because Cock Magic is a crutch.
		
		* Mysterion early is great, assuming your opponent doesn't have Medusa/Cock Magic/Transmog.
		* The best strategy was the deathball. Cycle your cards until you have PCP/Tupperware/Deckhand Butters.
		* Protect the Tupperware with spells, Heal PCP with Deckhand. Most people were running similar decks, but PCP was KEY for mirror matches.
		* Against decks with Transmog, I never played PCP.
		* In mirror matches, I wait for FB before I drop TnP.
		* Anyone not running adventure, is easy to 3-bar. A handful of opponents opened with YPC (they never had 10 energy - and never got ahead on energy compared to me - to play it again)... but he was easy enough to FB/LB before his slow warcry.
		* Against enemy tupperware, just drop 1 unit at a time, ideally an assassin.
		* Deckhand is also useful to heal your NK if your opponent tries to damage your new kid with only spells.
		* LB on HHC/Super Craig/Mosquito is definitely worth it.
		* FB+LB will kill PCP, but it's not enough value compared to taking out TnP with FB or a 3-cost fighter with LB.
		* Force yourself to let opponent's assassins get close to your NK, just so you can cycle Superfart. It's a situational spell that isn't easy to cycle when you're on the offensive.
		
		Good luck!
		
		![Challenge Deck](https://i.imgur.com/jor3ExN.png)
	
		Total Decks: 38, MMR Avg: 6073, MMR Standard Deviation: 612.7
		
		Percent | Themes
		------------ | -------------
		32% | adv,sup
		18% | adv,mys
		16% | adv,sci
		13% | mys,sci
		8% | adv,fan
		5% | mys,sup
		5% | fan,mys
		3% | adv,neu

		Percent | Cards
		------------ | -------------
		76% | Lightning Bolt
		76% | Fireball
		76% | Arrowstorm
		39% | Unholy Combustion
		39% | Terrance and Phillip
		39% | Calamity Heidi
		34% | Tupperware
		34% | Super Fart
		34% | Bandita Sally
		32% | Hallelujah
		26% | Mind Control
		26% | Hookhand Clyde
		26% | Hermes Kenny
		24% | Smuggler Ike
		24% | Regeneration
		24% | Mysterion
		24% | Chiorboy Butters
		21% | Super Craig
		21% | Inuit Kenny
		21% | Dogpoo
		18% | Poison
		18% | Mosquito
		18% | Energy Staff
		18% | Deckhand Butters
		16% | Space Warrior Token
		16% | Chomper
		16% | Astronaut Butters
		13% | Youth Pastor Craig
		13% | Warboy Tweek
		13% | Hyperdrive
		11% | Transmogrify
		11% | Rat Swarm
		11% | Professor Chaos
		11% | PC Principal
		11% | Lava!
		11% | Freeze Ray
		11% | Cyborg Kenny
		11% | Cock Magic
		11% | Captain Diabetes
		8% | Zen Cartman
		8% | Towelie
		8% | Program Stan
		8% | Priest Maxi
		8% | Paladin Butters
		8% | Enforcer Jimmy
		5% | Visitors
		5% | Underpants Gnomes
		5% | The Master Ninjew
		5% | The Amazingly Randy
		5% | Stan of Many Moons
		5% | President Garrison
		5% | Pope Timmy
		5% | Pocahontas Randy
		5% | Pigeon Gang
		5% | Nathan
		5% | Mr. Slave Executioner
		5% | Mimsy
		5% | Medusa Bebe
		5% | Marine Craig
		5% | Marcus
		5% | Chicken Coop
		5% | Big Gay Al
		3% | Witch Garrison
		3% | Toolshed
		3% | ThunderBird
		3% | The Coon
		3% | Swordsman Garrison
		3% | Storyteller Jimmy
		3% | Sorceress Liane
		3% | Sixth Element Randy
		3% | Shieldmaiden Wendy
		3% | Sheriff Cartman
		3% | Shaman Token
		3% | Sexy Nun Randy
		3% | Poseidon Stan
		3% | Pirate Ship Timmy
		3% | Officer Barbrady
		3% | Nelly
		3% | Mecha Timmy
		3% | Mayor McDaniels
		3% | Manbearpig
		3% | Le Bard Jimmy
		3% | Jesus
		3% | Incan Craig
		3% | Human Kite
		3% | Gunslinger Kyle
		3% | Grand Wizard Cartman
		3% | Gizmo Ike
		3% | General Disarray
		3% | Friar Jimmy
		3% | Doctor Timothy
		3% | Call Girl
		3% | Blood Elf Bebe
		3% | Barrel Dougie
		3% | Alien Drone
		3% | A.W.E.S.O.M.-O 4000
	''',lang_index))
	
def ChaosChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Decks I used. Butters,Dougies,Spells cost 1 less.
		
		12-1 over 3 runs with the same deck. I had several draws against similarly really cheap decks. More expensive decks never stood a chance.
		
		LB Doctor Timmy (or any 4-cost range unit) for +1 energy (I don't know why everyone kept playing their Doctor Timmy and losing 1 energy every time).
		Arrowstorm for visitors or paladin/dougie plays.
		Superfart for solo dougie play and you can drop another character to finish him off.
		Games are so fast paced with all the spam, it's easy to make a misplay. Know when to reset and when to spam. Most of my games went to overtime where I only got 1 bar.
		
		General Disarray, Professor Chaos, and Superfart are BY FAR the strongest cards in this challenge meta.
		My personal opinion is adventure has the best spells, ensuring you are always leading your opponent on energy.
		
		Good luck!
		
		![Challenge Deck](https://i.imgur.com/m6RZfpw.png)
	
		Total Decks: 41, MMR Avg: 6008, MMR Standard Deviation: 790.2
		
		Percent | Themes
		------------ | -------------
		17% | sci,sup
		17% | fan,sup
		15% | adv,sup
		12% | fan,sci
		10% | mys,sci
		10% | adv,sci
		10% | adv,fan
		7% | mys,sup
		2% | adv,mys
		
		Percent | Cards
		------------ | -------------
		51% | Professor Chaos
		44% | Terrance and Phillip
		44% | Mind Control
		41% | Super Fart
		41% | General Disarray
		39% | Paladin Butters
		34% | Visitors
		34% | Poison
		34% | Doctor Timothy
		32% | Astronaut Butters
		28% | Super Craig
		28% | Mosquito
		28% | Arrowstorm
		27% | Lightning Bolt
		24% | Warboy Tweek
		24% | Toolshed
		24% | Space Warrior Token
		22% | Powerfist Dougie
		22% | Dwarf Engineer Dougie
		22% | Blood Elf Bebe
		20% | Fireball
		17% | Tupperware
		17% | Transmogrify
		17% | Human Kite
		15% | Underpants Gnomes
		15% | Rat Swarm
		15% | Le Bard Jimmy
		15% | Freeze Ray
		15% | Dogpoo
		12% | Hookhand Clyde
		12% | Cyborg Kenny
		12% | Chiorboy Butters
		12% | Buccaneer Bebe
		10% | Witch Garrison
		10% | Unholy Combustion
		10% | Towelie
		10% | Stan of Many Moons
		10% | Pocahontas Randy
		10% | Nelly
		10% | Inuit Kenny
		10% | Deckhand Butters
		10% | Chomper
		10% | Barrel Dougie
		10% | Alien Drone
		7% | Swordsman Garrison
		7% | Robo Bebe
		7% | Regeneration
		7% | Prophet Dougie
		7% | Princess Kenny
		7% | Priest Maxi
		7% | Pigeon Gang
		7% | Mimsy
		7% | Medicine Woman Sharon
		7% | Hercules Clyde
		7% | Enforcer Jimmy
		7% | Captain Diabetes
		7% | Call Girl
		7% | Bounty Hunter Kyle
		5% | ThunderBird
		5% | The Coon
		5% | The Amazingly Randy
		5% | Sexy Nun Randy
		5% | Robin Tweek
		5% | Pope Timmy
		5% | PC Principal
		5% | Mr. Slave Executioner
		5% | Lava!
		5% | Hyperdrive
		5% | Hermes Kenny
		5% | Hallelujah
		5% | Fastpass
		5% | Cock Magic
		5% | Canadian Knight Ike
		5% | Big Mesquite Murph
		5% | Big Gay Al
		2% | Zen Cartman 1
		2% | Youth Pastor Craig 1
		2% | Swashbuckler Red 1
		2% | Starvin' Marvin 1
		2% | Santa Claus 1
		2% | Rogue Token 1
		2% | Program Stan 1
		2% | President Garrison 1
		2% | Nathan 1
		2% | Mysterion 1
		2% | Mr. Hankey 1
		2% | Mint-Berry Crunch 1
		2% | Medusa Bebe 1
		2% | Marine Craig 1
		2% | Marcus 1
		2% | Kyle of the Drow Elves 1
		2% | Jesus 1
		2% | Ice Sniper Wendy 1
		2% | Gunslinger Kyle 1
		2% | Friar Jimmy 1
		2% | Energy Staff 1
		2% | Dragonslayer Red 1
		2% | Catapult Timmy 1
		2% | Calamity Heidi 1
		2% | Bandita Sally 1
		2% | Angel Wendy 1
		2% | Alien Queen Red 1
	''',lang_index))
	
def NeutralChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Decks I used. Neutral Characters got a 30% boost to their stats.
		
		The meta was definitely different between silver shield and 7k. So I used two decks. Got 12 wins every other try.
		
		I had to use this deck in high legend to pull off 12 wins. Very diverse meta. Hard to get a high score.
		Watch out for Pope Timmy.
		Warboy was MVP. He gets so much value.
		DSR + LBJ combo helped a lot. Basically takes out TNP and most range units.
		Try to time transmog you kill a different unit just after, so they can't pope him.
		
		![Challenge Deck1](https://i.imgur.com/SSfwvhL.png)
		
		With all the DSR's, UC's, Transmog's and high skill players, this deck didn't work in Legend, but MBP+Pope shined in silver shield.
		Seemed to be countered by cheap decks with fast rotation and DSR.
		Lower skill players - means I was able to get a score in the top 50.
		Pope is still bugged. Opp transmogs MBP (only unit on the field) and a different card comes back.
		
		![Challenge Deck2](https://i.imgur.com/KWM7DAt.png)
	
		Total Decks: 63, MMR Avg: 5979, MMR Standard Deviation: 843.8

		Percent | Themes
		------------ | -------------
		16% | fan,sci
		11% | sci,sup
		11% | fan,sup
		10% | mys,sci
		8% | fan,mys
		8% | adv,sci
		6% | neu,neu
		6% | adv,mys
		5% | mys,neu
		5% | adv,fan
		3% | sci,neu
		3% | mys,sup
		3% | adv,sup
		2% | sup,neu
		2% | fan,neu
		2% | adv,neu

		Percent | Cards
		------------ | -------------
		73% | Dogpoo
		70% | Terrance and Phillip
		67% | Towelie
		59% | Nathan
		56% | Rat Swarm
		48% | PC Principal
		43% | Pigeon Gang
		38% | Blood Elf Bebe
		27% | Mimsy
		24% | Space Warrior Token
		22% | Visitors
		22% | President Garrison
		22% | Mr. Hankey
		22% | Mosquito
		21% | Paladin Butters
		21% | Manbearpig
		19% | Terrance Mephesto
		19% | Professor Chaos
		17% | Warboy Tweek
		17% | Santa Claus
		16% | Unholy Combustion
		16% | Poison
		16% | Le Bard Jimmy
		14% | Mr. Mackey
		14% | Marcus
		14% | Dragonslayer Red
		13% | Super Craig
		13% | Princess Kenny
		13% | Pope Timmy
		13% | Nelly
		13% | Energy Staff
		13% | Bounty Hunter Kyle
		11% | Tupperware
		11% | Transmogrify
		11% | Lightning Bolt
		11% | Doctor Timothy
		10% | Witch Garrison
		10% | Underpants Gnomes
		10% | Mayor McDaniels
		10% | Inuit Kenny
		10% | Big Gay Al
		8% | Super Fart
		8% | Mind Control
		8% | Medicine Woman Sharon
		8% | Human Kite
		8% | General Disarray
		8% | Catapult Timmy
		8% | Alien Drone
		6% | The Master Ninjew
		6% | Starvin' Marvin
		6% | Officer Barbrady
		6% | Marine Craig
		6% | Hookhand Clyde
		6% | Hermes Kenny
		6% | Cyborg Kenny
		5% | Sexy Nun Randy
		5% | Regeneration
		5% | Program Stan
		5% | Pocahontas Randy
		5% | Hyperdrive
		5% | Fastpass
		5% | Enforcer Jimmy
		5% | Elven King Bradley
		5% | Classi
		5% | Chiorboy Butters
		5% | Arrowstorm
		3% | Zen Cartman
		3% | ThunderBird
		3% | The Coon
		3% | The Amazingly Randy
		3% | Stan the Great
		3% | Satan
		3% | Robo Bebe
		3% | Prophet Dougie
		3% | Priest Maxi
		3% | Powerfist Dougie
		3% | Hallelujah
		3% | Deckhand Butters
		3% | Buccaneer Bebe
		2% | Wonder Tweek 1
		2% | Witch Doctor Token 1
		2% | Toolshed 1
		2% | Swashbuckler Red 1
		2% | Storyteller Jimmy 1
		2% | Stan of Many Moons 1
		2% | Sorceress Liane 1
		2% | Smuggler Ike 1
		2% | Sharpshooter Shelly 1
		2% | Purify 1
		2% | Power Bind 1
		2% | Mysterion 1
		2% | Mr. Slave Executioner 1
		2% | Medusa Bebe 1
		2% | Mecha Timmy 1
		2% | Kyle of the Drow Elves 1
		2% | Jesus 1
		2% | Ice Sniper Wendy 1
		2% | Grand Wizard Cartman 1
		2% | Gizmo Ike 1
		2% | Friar Jimmy 1
		2% | Cupid Cartman 1
		2% | Captain Diabetes 1
		2% | Calamity Heidi 1
		2% | Astronaut Butters 1
		2% | Alien Clyde 1
		
	''',lang_index))

def InanimateChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Deck I used. These cards cost 1:
		   * Chicken Coop
		   * Energy Staff
		   * Alien Drone
		   * Chomper
		   * Lava!
		   * ThunderBird
		
		Managed to get 12-1 over 3 runs. Almost every game I got down to 1 to 4 cards in my hand. Deck is much closer to 2.0 cost if you pull off the Hermes/Staff combo, especially in the last minute. I managed to pull off hermes deathwish 3 times over the duration of 1 staff, but generally it was just 1 or 2.
		
		Strategies to do or watch out for:
		
		Have Staff ready before Hermes dies.
		Go for the draw. Hermes/Staff is BANANAS in the last minute.
		The other cards should be obvious, like Zen to protect, Visitors to melt.
		Deck so cheap you can spam wide when you're ahead on energy.
		
		DSR -> LBJ gets huge value, but my deck cycles so fast.
		Poison -> LBJ will kill Mecha Timmy, but he pops right back in my hand.
		
		The meta deck was definitely fan/sci, but I still feel like mystical staff was stronger. Opponents running Adventure was the easiest to take out, because EJ/Zen makes their Thunderbird a waste of 1 energy.
		
		![Challenge Deck](https://i.imgur.com/SHcNvgz.png)
	
		Total Decks: 39, MMR Avg: 5745, MMR Standard Deviation: 998.2

		Percent | Themes
		------------ | -------------
		26% | fan,sci
		13% | sci,sup
		13% | fan,mys
		10% | mys,sup
		8% | mys,sci
		8% | fan,sup
		8% | adv,sci
		8% | adv,mys
		5% | adv,sup
		3% | adv,fan

		Percent | Cards
		------------ | -------------
		51% | Terrance and Phillip
		44% | Blood Elf Bebe
		41% | Space Warrior Token
		41% | Chicken Coop
		41% | Alien Drone
		36% | Visitors
		36% | Energy Staff
		31% | Underpants Gnomes
		31% | Mosquito
		31% | Doctor Timothy
		28% | Lava!
		28% | Chomper
		26% | Warboy Tweek
		26% | Hermes Kenny
		23% | Enforcer Jimmy
		23% | Dragonslayer Red
		23% | Dogpoo
		18% | Zen Cartman
		18% | Tupperware
		18% | Super Fart
		18% | Super Craig
		18% | Rat Swarm
		18% | Pope Timmy
		18% | Poison
		18% | Paladin Butters
		18% | Le Bard Jimmy
		15% | Toolshed
		15% | ThunderBird
		15% | Professor Chaos
		15% | Nathan
		13% | Witch Garrison
		13% | Unholy Combustion
		13% | Towelie
		13% | Human Kite
		10% | The Amazingly Randy
		10% | Power Bind
		10% | Mimsy
		10% | Medicine Woman Sharon
		10% | Lightning Bolt
		10% | Hookhand Clyde
		10% | Fastpass
		10% | Chiorboy Butters
		10% | Catapult Timmy
		10% | Bounty Hunter Kyle
		10% | Astronaut Butters
		8% | Transmogrify
		8% | Stan of Many Moons
		8% | Sexy Nun Randy
		8% | Santa Claus
		8% | Princess Kenny
		8% | Pigeon Gang
		8% | Mr. Slave Executioner
		8% | Mind Control
		8% | Medusa Bebe
		8% | Inuit Kenny
		8% | Arrowstorm
		5% | Wonder Tweek
		5% | Witch Doctor Token
		5% | The Coon
		5% | Robo Bebe
		5% | Program Stan
		5% | Priest Maxi
		5% | Powerfist Dougie
		5% | Pocahontas Randy
		5% | PC Principal
		5% | Mysterion
		5% | Mecha Timmy
		5% | Manbearpig
		5% | Jesus
		5% | Gunslinger Kyle
		5% | Elven King Bradley
		5% | Cyborg Kenny
		5% | Captain Diabetes
		5% | Alien Clyde
		3% | The Master Ninjew
		3% | Terrance Mephesto
		3% | Swordsman Garrison
		3% | Storyteller Jimmy
		3% | Starvin' Marvin
		3% | Sizzler Stuart
		3% | Shieldmaiden Wendy
		3% | Sheriff Cartman
		3% | Sharpshooter Shelly
		3% | Rogue Token
		3% | Prophet Dougie
		3% | President Garrison
		3% | Mr. Hankey
		3% | Marcus
		3% | Kyle of the Drow Elves
		3% | Ice Sniper Wendy
		3% | Hyperdrive
		3% | Hallelujah
		3% | Grand Wizard Cartman
		3% | Gizmo Ike
		3% | Dwarf Engineer Dougie
		3% | Deckhand Butters
		3% | Cupid Cartman
		3% | Canadian Knight Ike
		3% | Call Girl
		3% | Big Mesquite Murph
		3% | Barrel Dougie
		3% | Bandita Sally
		3% | Alien Queen Red
		3% | A.W.E.S.O.M.-O 4000
		
	''',lang_index))

def BigBoyChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Deck I used. Tanks have 2x health and 30% attack boost, making the roughly equivalent to the same card at +FF Levels (Level 2 epic -> L4 epic, Level 3 rare -> Level 5 rare)
		
		Managed to get 11-12 wins over 3 runs, and only several losses to bugs in the game. UC Pope Timmy before his warcry, and a full second after enemy pope dies then his warcry goes off. Also, a couple of transmogs that highlighted the correct target, but transmog'd a different target: TRIPLE CHECK your transmog area.
		Had 1 legit loss where range units targetted opp tank and then they ninjewed their pigeons. Holy crap, was not expecting that.
		
		![Challenge Deck](https://i.imgur.com/oVzcI03.png)
		
		I've gotta say, every opponent was playing something fresh. Never knew whether to expect pope timmy/DSR/LBJ/Pigeons.
		
		DSR was too weak, because it costs 4 energy and just puts the tanks at their normal health. I beat one opponent who DSR'd my tanks and backline 3 times before I finally pushed through.
		Double hard removal was great. Using a removal on Zen/PCP is justified, otherwise not recommended.
		Watch out for the pope play, I generally tried to deny it by removing the tank then killing another unit ASAP OR UC the pope before warcry (transmog too slow).
		Save your removal for when you need it. Don't rush to use it at first site.
		Mimsy is decent, but he can be killed with units before he takes a bar.
		Save Liane for when opp tank(s) are on your side, and you can send catapult's rats or amazingly's cocks into her, because it's too easy for opp to UC her and her deathwish is wasted. She only transforms 2 units so watch out for swarms.
	
		Total Decks: 39, MMR Avg: 5273, MMR Standard Deviation: 1400.3

		Percent | Themes
		------------ | -------------
		26% | fan,mys
		15% | adv,mys
		13% | adv,fan
		10% | mys,sup
		10% | adv,sup
		8% | mys,sci
		5% | sci,sup
		5% | fan,sci
		5% | adv,sci
		3% | fan,sup

		Percent | Cards
		------------ | -------------
		49% | Mimsy
		41% | Priest Maxi
		38% | Unholy Combustion
		38% | PC Principal
		36% | Zen Cartman
		36% | Pope Timmy
		36% | Manbearpig
		36% | Energy Staff
		36% | Dogpoo
		31% | Terrance and Phillip
		31% | Rat Swarm
		28% | Blood Elf Bebe
		26% | Pigeon Gang
		26% | Nathan
		26% | Mr. Slave Executioner
		26% | Hermes Kenny
		23% | Transmogrify
		23% | Dragonslayer Red
		23% | Chiorboy Butters
		18% | Underpants Gnomes
		18% | Super Craig
		18% | Santa Claus
		18% | Paladin Butters
		18% | Inuit Kenny
		15% | Stan of Many Moons
		15% | Mosquito
		15% | Cyborg Kenny
		13% | Toolshed
		13% | The Coon
		13% | Sheriff Cartman
		13% | Professor Chaos
		13% | Human Kite
		13% | Fastpass
		10% | Warboy Tweek
		10% | Visitors
		10% | ThunderBird
		10% | Program Stan
		10% | Hookhand Clyde
		10% | Grand Wizard Cartman
		10% | Doctor Timothy
		10% | Big Mesquite Murph
		8% | Wonder Tweek
		8% | The Master Ninjew
		8% | Swordsman Garrison
		8% | Super Fart
		8% | Sorceress Liane
		8% | Sexy Nun Randy
		8% | Rogue Token
		8% | Prophet Dougie
		8% | Princess Kenny
		8% | Pocahontas Randy
		8% | Mind Control
		8% | Medicine Woman Sharon
		8% | Lightning Bolt
		8% | Lava!
		8% | Hallelujah
		8% | Cock Magic
		8% | Arrowstorm
		8% | A.W.E.S.O.M.-O 4000
		5% | Witch Garrison
		5% | Towelie
		5% | The Amazingly Randy
		5% | Terrance Mephesto
		5% | Storyteller Jimmy
		5% | Space Warrior Token
		5% | Robo Bebe
		5% | Officer Barbrady
		5% | Mysterion
		5% | Mr. Hankey
		5% | Mint-Berry Crunch
		5% | Hercules Clyde
		5% | Friar Jimmy
		5% | Fireball
		5% | Deckhand Butters
		5% | Catapult Timmy
		5% | Canadian Knight Ike
		5% | Bounty Hunter Kyle
		3% | Youth Pastor Craig
		3% | Tupperware
		3% | Swashbuckler Red
		3% | Smuggler Ike
		3% | Shieldmaiden Wendy
		3% | Scout Ike
		3% | Robin Tweek
		3% | Poison
		3% | Mr. Mackey
		3% | Mecha Timmy
		3% | Marcus
		3% | Le Bard Jimmy
		3% | Kyle of the Drow Elves
		3% | Hyperdrive
		3% | Gizmo Ike
		3% | Four-Assed Monkey
		3% | Dwarf Engineer Dougie
		3% | Cupid Cartman
		3% | Classi
		3% | Chicken Coop
		3% | Captain Diabetes
		3% | Call Girl
		3% | Calamity Heidi
		3% | Buccaneer Bebe
		3% | Barrel Dougie
		3% | Astronaut Butters
		
	''',lang_index))
	
def CommonChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Deck I used.
		
		Managed to get 12 wins over 3 runs, and only 1 loss to someone who had a better cycle than me. Got in the top 50 on the leaderboard as well.
		
		![Challenge Deck](https://i.imgur.com/RMK7KWu.png)
		
		I've gotta say, most opponents were not playing a 'meta deck'.
		
		Doctor Timothy was way too powerful to pass up this meta.
		Mimsy was garbage. Most games he never managed to even touch my NK.
		Mackey was OP, since 9 cards are kids, AND a boost to your NK zap. Mackey Combo with Range or SuperCraig is even more broken.
		Adventure has potential, but overall it's still too weak compared to fantasy and/or superheros.
	
		Total Decks: 37, MMR Avg: 4763, MMR Standard Deviation: 2077.3

		Percent | Themes
		------------ | -------------
		24% | fan,sup
		16% | adv,fan
		11% | sci,sup
		11% | fan,mys
		11% | adv,sup
		11% | adv,sci
		5% | fan,sci
		5% | adv,mys
		3% | mys,sup
		3% | mys,sci

		Percent | Cards
		------------ | -------------
		68% | Terrance and Phillip
		54% | Le Bard Jimmy
		49% | Rat Swarm
		49% | Blood Elf Bebe
		46% | Super Craig
		43% | Tupperware
		43% | Stan the Great
		41% | Paladin Butters
		41% | Mimsy
		41% | Captain Diabetes
		38% | Princess Kenny
		38% | Pigeon Gang
		30% | Mr. Mackey
		27% | Calamity Heidi
		24% | Gunslinger Kyle
		24% | Doctor Timothy
		22% | Dogpoo
		19% | Super Fart
		19% | Deckhand Butters
		16% | Smuggler Ike
		14% | Unholy Combustion
		14% | Robo Bebe
		14% | Robin Tweek
		14% | Poison
		14% | Outlaw Tweek
		14% | Nathan
		14% | Bandita Sally
		11% | Warboy Tweek
		11% | Swordsman Garrison
		11% | Poseidon Stan
		11% | Lava!
		11% | Friar Jimmy
		11% | Astronaut Butters
		11% | Alien Clyde
		8% | Zen Cartman
		8% | Towelie
		8% | The Amazingly Randy
		8% | Space Warrior Token
		8% | Professor Chaos
		8% | Pocahontas Randy
		8% | Mosquito
		8% | Medicine Woman Sharon
		8% | Marine Craig
		8% | Hookhand Clyde
		8% | Hermes Kenny
		8% | Hallelujah
		8% | Fireball
		8% | Big Gay Al
		8% | Angel Wendy
		5% | Underpants Gnomes
		5% | Toolshed
		5% | Storyteller Jimmy
		5% | Stan of Many Moons
		5% | Shaman Token
		5% | Sexy Nun Randy
		5% | Scout Ike
		5% | Priest Maxi
		5% | Pope Timmy
		5% | Mind Control
		5% | Lightning Bolt
		5% | Dwarf Engineer Dougie
		5% | Dragonslayer Red
		5% | Chiorboy Butters
		5% | Catapult Timmy
		5% | Canadian Knight Ike
		5% | Bounty Hunter Kyle
		3% | Wonder Tweek
		3% | Witch Garrison
		3% | Transmogrify
		3% | The Coon
		3% | Terrance Mephesto
		3% | Starvin' Marvin
		3% | Sorceress Liane
		3% | Sheriff Cartman
		3% | Rogue Token
		3% | Purify
		3% | Prophet Dougie
		3% | Mr. Slave Executioner
		3% | Mr. Hankey
		3% | Marcus
		3% | Manbearpig
		3% | Kyle of the Drow Elves
		3% | Hyperdrive
		3% | Human Kite
		3% | Hercules Clyde
		3% | Gizmo Ike
		3% | Fastpass
		3% | Energy Staff
		3% | Elven King Bradley
		3% | Dwarf King Clyde
		3% | Dark Mage Craig
		3% | Cyborg Kenny
		3% | Cupid Cartman
		3% | Buccaneer Bebe
		3% | Barrel Dougie
		3% | Arrowstorm
		3% | Alien Queen Red
		3% | Alien Drone
		
	''',lang_index))

def WheelOfFortuneChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Deck I used.
		
		Managed to go 12-0 across 2 runs, got 1 match that never started and counted as a loss... Got ~1350 in my best run, but that only landed me around 800.
		
		![Challenge Deck](https://i.imgur.com/t0FFCku.png)
		
		I've gotta say, opponents across all my runs didn't have a strong 'meta' deck. This deck isn't the best, but it beat every deck I faced.
		
		The key was 'punish'. If they have gnomes, wait until after they drop it to play Liane. If you don't know, when you do play liane, have your gnomes behind her. If they have arrowstorm/outlaw tweek - wait until after they drop him to play visitors and spam assassins.
		
		A well-timed Warboy Tweek at 2 cost is probably what beat my tougher opponents. Alien Clyde was decent. President Garrison was RNG, but played enough games he gets amazing value. Garrison paired with LBJ, it does some serious damage.
		
		I rarely played poison, but it was key to stop shenanigans like Santa/SOMM/KOTDE/Dougie.
		
	
		Total Decks: 24, MMR Avg: 6119, MMR Standard Deviation: 714.2

		Percent | Themes
		------------ | -------------
		25% | fan,sci
		25% | adv,sci
		12% | sci,sup
		12% | fan,sup
		8% | mys,sci
		8% | adv,sup
		4% | adv,mys
		4% | adv,fan

		Percent | Cards
		------------ | -------------
		46% | Warboy Tweek
		46% | Visitors
		46% | Four-Assed Monkey
		46% | Alien Clyde
		42% | Terrance and Phillip
		42% | Space Warrior Token
		33% | Hookhand Clyde
		33% | Dogpoo
		28% | President Garrison
		28% | Enforcer Jimmy
		25% | Stan of Many Moons
		25% | Professor Chaos
		25% | Poison
		25% | Paladin Butters
		25% | Mosquito
		25% | Doctor Timothy
		25% | Blood Elf Bebe
		21% | Underpants Gnomes
		21% | Lightning Bolt
		17% | Mysterion
		17% | Medicine Woman Sharon
		17% | Dwarf Engineer Dougie
		17% | Cyborg Kenny
		17% | Cock Magic
		12% | Towelie
		12% | Toolshed
		12% | Swordsman Garrison
		12% | Super Craig
		12% | Sorceress Liane
		12% | Sheriff Cartman
		12% | Program Stan
		12% | Princess Kenny
		12% | Powerfist Dougie
		12% | Nathan
		12% | Human Kite
		12% | Hermes Kenny
		12% | Call Girl
		12% | Calamity Heidi
		12% | Bounty Hunter Kyle
		12% | Barrel Dougie
		12% | Astronaut Butters
		12% | Arrowstorm
		8% | Tupperware
		8% | Super Fart
		8% | Starvin' Marvin
		8% | Sixth Element Randy
		8% | Santa Claus
		8% | Robin Tweek
		8% | Rat Swarm
		8% | Pigeon Gang
		8% | PC Principal
		8% | Outlaw Tweek
		8% | Mint-Berry Crunch
		8% | Mind Control
		8% | Mecha Timmy
		8% | Marcus
		8% | Kyle of the Drow Elves
		8% | Inuit Kenny
		8% | Grand Wizard Cartman
		8% | Fastpass
		8% | Deckhand Butters
		8% | Chomper
		8% | Chiorboy Butters
		8% | Alien Drone
		4% | Zen Cartman
		4% | Witch Doctor Token
		4% | Unholy Combustion
		4% | The Coon
		4% | The Amazingly Randy
		4% | Stan the Great
		4% | Smuggler Ike
		4% | Rogue Token
		4% | Regeneration
		4% | Purify
		4% | Prophet Dougie
		4% | Pocahontas Randy
		4% | Nelly
		4% | Mr. Slave Executioner
		4% | Mr. Hankey
		4% | Mimsy
		4% | Medusa Bebe
		4% | Manbearpig
		4% | Hercules Clyde
		4% | Dragonslayer Red
		4% | Captain Diabetes
		4% | Canadian Knight Ike
		4% | Buccaneer Bebe
		4% | Bandita Sally
		
	''',lang_index))
	
def PilgrimChallenge2(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Deck I used.
		
		Managed to go 12-0 and 10-1, before getting 2 disconnects, getting a spot in the top 50.
		
		![Challenge Deck](https://i.imgur.com/P3IARCR.png)
		
		The key is a properly timed FB. I normally try to use it on MWS + 1 or 2 other units.
		Save Inuit Kenny for SOMM. Have Gnomes ready to counter opponent's inuit. Don't go all in unless you know they don't have arrowstorm.
		Incan craig was too weak with his warcry, and he will instantly die if he hits Inuit.
		My 1 loss was due to someone who had better cycle.
		Big Mesquite Murph has an insane amount of health. DSR every time.
		Your opponent may or may not run LB and/or FB. Take advantage of the negative energy trade and drop him in the back when you're making a push. Watch out a sneaky Inuit rush.
	
		Total Decks: 25, MMR Avg: 5888, MMR Standard Deviation: 765.4

		Percent | Themes
		------------ | -------------
		28% | adv,fan
		24% | adv,sup
		16% | adv,sci
		16% | adv,mys
		12% | adv,neu
		4% | fan,mys

		Percent | Cards
		------------ | -------------
		80% | Pocahontas Randy
		76% | Medicine Woman Sharon
		72% | Stan of Many Moons
		68% | Inuit Kenny
		48% | Storyteller Jimmy
		48% | Bandita Sally
		44% | Calamity Heidi
		40% | Sheriff Cartman
		36% | Arrowstorm
		32% | Fireball
		28% | Terrance and Phillip
		28% | Lightning Bolt
		24% | Tupperware
		24% | Sharpshooter Shelly
		24% | Hookhand Clyde
		24% | Blood Elf Bebe
		20% | Mosquito
		20% | Dogpoo
		16% | Space Warrior Token
		16% | Le Bard Jimmy
		16% | Incan Craig
		16% | Human Kite
		16% | Gunslinger Kyle
		16% | Dragonslayer Red
		16% | Big Mesquite Murph
		16% | Barrel Dougie
		12% | Visitors
		12% | Toolshed
		12% | Santa Claus
		12% | Professor Chaos
		12% | Poison
		12% | Pigeon Gang
		12% | Outlaw Tweek
		12% | Nathan
		12% | Doctor Timothy
		12% | Buccaneer Bebe
		8% | Unholy Combustion
		8% | Terrance Mephesto
		8% | Swordsman Garrison
		8% | Super Craig
		8% | PC Principal
		8% | Kyle of the Drow Elves
		8% | Enforcer Jimmy
		8% | Energy Staff
		8% | Deckhand Butters
		8% | Chiorboy Butters
		4% | Zen Cartman
		4% | Warboy Tweek
		4% | Towelie
		4% | The Master Ninjew
		4% | The Coon
		4% | The Amazingly Randy
		4% | Swashbuckler Red
		4% | Super Fart
		4% | Smuggler Ike
		4% | Shieldmaiden Wendy
		4% | Shaman Token
		4% | Sexy Nun Randy
		4% | Rat Swarm
		4% | Prophet Dougie
		4% | Princess Kenny
		4% | Power Bind
		4% | Pope Timmy
		4% | Pirate Ship Timmy
		4% | Paladin Butters
		4% | Officer Barbrady
		4% | Mint-Berry Crunch
		4% | Mind Control
		4% | Manbearpig
		4% | Jesus
		4% | Imp Tweek
		4% | Hercules Clyde
		4% | Hallelujah
		4% | Elven King Bradley
		4% | Dwarf Engineer Dougie
		4% | Cupid Cartman
		4% | Chicken Coop
		4% | Catapult Timmy
		4% | Captain Diabetes
		4% | Big Gay Al
		
	''',lang_index))

def WrapUp2019Challenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Deck I used.
		
		Very Tough Week! Managed 12-2, mostly by 1 bar, had a few draws.
		Also did 1 run with a different deck and got destroyed.
		
		This is the deck I used. It is by no means a good deck. I started 3-2, then finished 12-2 once I got the hang of it, but it takes skill to know when to go all-in. Know when to use poison and other cards. Play Mysterion as early as possible. Most of my matches ended in a draw or I got 1 bar in overtime. Luckily it was so cheap I could cycle poison quickly enough to take out Mint-Berry Crunch and play it again on Human Kite, but Human Kite is always the primary target no matter what.
		
		I lost to 1 deck because of a bad opening. If I can open with Mysterion, then Doctor Timothy, it's a guaranteed win for me...
		
		![Challenge Deck](https://i.imgur.com/KLNxdN1.png)
	
		Total Decks: 22, MMR Avg: 6035, MMR Standard Deviation: 1302.2

		Percent | Themes
		------------ | -------------
		27% | sci,sup
		27% | fan,sup
		14% | adv,sup
		9% | sup,neu
		5% | mys,sup
		5% | fan,sci
		5% | adv,sci
		5% | adv,mys
		5% | adv,fan

		Percent | Cards
		------------ | -------------
		82% | Professor Chaos
		82% | Doctor Timothy
		77% | Toolshed
		77% | Mosquito
		64% | Mysterion
		64% | Human Kite
		64% | Captain Diabetes
		55% | Super Fart
		45% | Tupperware
		36% | The Coon
		36% | Fastpass
		32% | Dragonslayer Red
		27% | Mint-Berry Crunch
		23% | Poison
		23% | Le Bard Jimmy
		23% | Chomper
		23% | Call Girl
		23% | Blood Elf Bebe
		18% | Visitors
		14% | Terrance and Phillip
		14% | Pigeon Gang
		14% | Lightning Bolt
		14% | Elven King Bradley
		14% | Dogpoo
		14% | Deckhand Butters
		14% | Calamity Heidi
		9% | The Amazingly Randy
		9% | Stan of Many Moons
		9% | Space Warrior Token
		9% | Santa Claus
		9% | Mr. Slave Executioner
		9% | Medicine Woman Sharon
		9% | Hookhand Clyde
		9% | Four-Assed Monkey
		9% | Arrowstorm
		5% | Witch Garrison
		5% | Unholy Combustion
		5% | Towelie
		5% | Terrance Mephesto
		5% | Swordsman Garrison
		5% | Swashbuckler Red
		5% | Sorceress Liane
		5% | Smuggler Ike
		5% | Sheriff Cartman
		5% | Rogue Token
		5% | Robo Bebe
		5% | Rat Swarm
		5% | Program Stan
		5% | President Garrison
		5% | Pocahontas Randy
		5% | Paladin Butters
		5% | PC Principal
		5% | Nathan
		5% | Mind Control
		5% | Medusa Bebe
		5% | Mayor McDaniels
		5% | Jesus
		5% | Gunslinger Kyle
		5% | Fireball
		5% | Dwarf King Clyde
		5% | Dwarf Engineer Dougie
		5% | Dark Mage Craig
		5% | Cyborg Kenny
		5% | Classi
		5% | Buccaneer Bebe
		5% | Bounty Hunter Kyle
		5% | Bandita Sally
		5% | Alien Clyde
	''',lang_index))
	
def CraigTweekChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Deck I used.
		
		Very Tough Week! Managed 12-2, mostly by 1 bar, had a few draws.
		Also did 1 run with a different deck and actually got 12 wins at a lower rank.
		
		If you use my deck, play mysterion early. I generally won 1-0 in overtime or the opponent took a bar first and then I came back.
		
		Double Tweek was no problem, they are both boosted and both have a time and place. Swarm of fighters? Now they are stuck with wonder tweek. Combo with Chaos and you ruin their push.
		
		Terrance and phillip were great this challenge, but I needed really fast cycle to always have an answer.
		
		![Challenge Deck](https://i.imgur.com/nyKBoQB.png)
	
		Total Decks: 26, MMR Avg: 5210, MMR Standard Deviation: 1739.2

		Percent | Themes
		------------ | -------------
		57% | sci,sup
		15% | fan,sup
		12% | adv,sup
		4% | sup,neu
		4% | mys,sci
		4% | fan,mys
		4% | adv,sci

		Percent | Cards
		------------ | -------------
		69% | Super Craig
		69% | Mosquito
		62% | Professor Chaos
		62% | Doctor Timothy
		54% | Terrance and Phillip
		50% | Warboy Tweek
		42% | Wonder Tweek
		42% | Visitors
		42% | Human Kite
		38% | Tupperware
		35% | Dogpoo
		31% | Super Fart
		31% | Mysterion
		27% | Space Warrior Token
		27% | Bounty Hunter Kyle
		23% | Poison
		19% | Toolshed
		19% | The Coon
		19% | Nathan
		19% | Fastpass
		15% | Program Stan
		15% | Alien Drone
		12% | Underpants Gnomes
		12% | Towelie
		12% | Stan of Many Moons
		12% | Sizzler Stuart
		12% | Mecha Timmy
		12% | Marine Craig
		12% | Lava!
		12% | Enforcer Jimmy
		12% | Cyborg Kenny
		12% | Call Girl
		8% | Unholy Combustion
		8% | Swordsman Garrison
		8% | Santa Claus
		8% | Robo Bebe
		8% | Robin Tweek
		8% | Princess Kenny
		8% | Powerfist Dougie
		8% | Pocahontas Randy
		8% | Pigeon Gang
		8% | Lightning Bolt
		8% | Le Bard Jimmy
		8% | Gizmo Ike
		8% | Captain Diabetes
		8% | Blood Elf Bebe
		8% | Big Gay Al
		8% | A.W.E.S.O.M.-O 4000
		4% | Zen Cartman
		4% | Youth Pastor Craig
		4% | The Amazingly Randy
		4% | Swashbuckler Red
		4% | Storyteller Jimmy
		4% | Smuggler Ike
		4% | Sixth Element Randy
		4% | Shieldmaiden Wendy
		4% | Sheriff Cartman
		4% | Sexy Nun Randy
		4% | Rat Swarm
		4% | Purify
		4% | Priest Maxi
		4% | President Garrison
		4% | Pope Timmy
		4% | Paladin Butters
		4% | Outlaw Tweek
		4% | Officer Barbrady
		4% | Mr. Slave Executioner
		4% | Mint-Berry Crunch
		4% | Mind Control
		4% | Mimsy
		4% | Medusa Bebe
		4% | Kyle of the Drow Elves
		4% | Inuit Kenny
		4% | Incan Craig
		4% | Imp Tweek
		4% | Hookhand Clyde
		4% | Hallelujah
		4% | Grand Wizard Cartman
		4% | Fireball
		4% | Energy Staff
		4% | Dwarf Engineer Dougie
		4% | Dragonslayer Red
		4% | Dark Mage Craig
		4% | Chomper
		4% | Captain Wendy
		4% | Astronaut Butters
		4% | Alien Queen Red
	''',lang_index))
	
def ElectricChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Deck I used.
		
		Owned it! Managed 12-0, mostly by 1 bar, had 1 draw.
		Also did 1 run with a different deck and got destroyed.
		
		Play it slow and Mysterion gets great value the longer he's alive.
		Combo Freeze wins games -> Sizzler Stuart, 3 seconds later Chaos.
		
		![Challenge Deck](https://i.imgur.com/1kUbJEG.png)
	
		Total Decks: 20, MMR Avg: 5338, MMR Standard Deviation: 2090.3

		Percent | Themes
		------------ | -------------
		45% | sci,sup
		20% | fan,sup
		15% | adv,sup
		10% | adv,sci
		5% | fan,mys
		5% | adv,fan

		Percent | Cards
		------------ | -------------
		80% | Mosquito
		65% | Professor Chaos
		60% | Terrance and Phillip
		60% | Human Kite
		60% | Fastpass
		55% | Doctor Timothy
		55% | Chomper
		40% | Visitors
		40% | Sizzler Stuart
		40% | Mysterion
		35% | Poison
		30% | Warboy Tweek
		30% | Space Warrior Token
		25% | Captain Diabetes
		20% | Tupperware
		20% | Toolshed
		20% | Pocahontas Randy
		20% | Medicine Woman Sharon
		20% | Dogpoo
		20% | Call Girl
		15% | Underpants Gnomes
		15% | Stan of Many Moons
		15% | Santa Claus
		15% | Princess Kenny
		15% | Mimsy
		15% | Lava!
		15% | Enforcer Jimmy
		15% | Blood Elf Bebe
		10% | Towelie
		10% | The Amazingly Randy
		10% | Swordsman Garrison
		10% | Super Fart
		10% | Rogue Token
		10% | Program Stan
		10% | Nathan
		10% | Lightning Bolt
		10% | Le Bard Jimmy
		10% | Dwarf Engineer Dougie
		10% | Cyborg Kenny
		10% | Big Gay Al
		10% | Arrowstorm
		5% | Zen Cartman
		5% | Transmogrify
		5% | The Coon
		5% | Swashbuckler Red
		5% | Smuggler Ike
		5% | Sheriff Cartman
		5% | Sharpshooter Shelly
		5% | Robo Bebe
		5% | Robin Tweek
		5% | Priest Maxi
		5% | Pirate Ship Timmy
		5% | Pigeon Gang
		5% | Paladin Butters
		5% | PC Principal
		5% | Mr. Mackey
		5% | Mind Control
		5% | Mecha Timmy
		5% | Manbearpig
		5% | Gizmo Ike
		5% | Friar Jimmy
		5% | Elven King Bradley
		5% | Dragonslayer Red
		5% | Deckhand Butters
		5% | Dark Mage Craig
		5% | Cock Magic
		5% | Canadian Knight Ike
		5% | Bounty Hunter Kyle
		5% | Big Mesquite Murph
		5% | Barrel Dougie
		5% | Bandita Sally
		5% | Alien Clyde
		
	''',lang_index))
	
def SpellbendersChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Deck I used.
		
		Owned it! Managed 12-1, mostly 1-0.
		
		PCP was critical in the mirror matches (and NO ONE ran PCP in my mirror matches). Protect the Tupperware AND Protect the PCP (with deckhand).
		
		![Challenge Deck](https://i.imgur.com/lVncYAj.png)
	
		Total Decks: 13, MMR Avg: 6247, MMR Standard Deviation: 916.7

		Percent | Themes
		------------ | -------------
		46% | adv,sup
		31% | adv,mys
		8% | fan,mys
		8% | adv,sci
		8% | adv,fan

		Percent | Cards
		------------ | -------------
		85% | Lightning Bolt
		85% | Arrowstorm
		77% | Fireball
		54% | Smuggler Ike
		54% | Calamity Heidi
		46% | Tupperware
		46% | Super Fart
		46% | Mysterion
		46% | Hookhand Clyde
		38% | Dogpoo
		38% | Bandita Sally
		31% | Terrance and Phillip
		31% | Mosquito
		31% | Hallelujah
		31% | Deckhand Butters
		31% | Captain Diabetes
		23% | Regeneration
		23% | Mimsy
		23% | Chiorboy Butters
		15% | Zen Cartman
		15% | Unholy Combustion
		15% | Transmogrify
		15% | Priest Maxi
		15% | Pope Timmy
		15% | Pocahontas Randy
		15% | Marcus
		15% | Hermes Kenny
		15% | Energy Staff
		15% | Chicken Coop
		8% | Witch Doctor Token
		8% | Underpants Gnomes
		8% | Towelie
		8% | The Amazingly Randy
		8% | Swashbuckler Red
		8% | Stan of Many Moons
		8% | Sharpshooter Shelly
		8% | Santa Claus
		8% | Rogue Token
		8% | Rat Swarm
		8% | Purify
		8% | Professor Chaos
		8% | Princess Kenny
		8% | Power Bind
		8% | Poison
		8% | Paladin Butters
		8% | Outlaw Tweek
		8% | Nathan
		8% | Mr. Hankey
		8% | Inuit Kenny
		8% | Hyperdrive
		8% | Cock Magic
		8% | Chomper
		8% | Bounty Hunter Kyle
		8% | Blood Elf Bebe
		8% | Big Mesquite Murph
		8% | Big Gay Al
		
	''',lang_index))

def RangersChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Deck I used.
		
		Got wrecked. Managed 10-3 on my best run. Faced way too many 7500+.
		
		![Challenge Deck](https://i.imgur.com/JhPBWqj.png)
	
		Total Decks: 32, MMR Avg: 6326, MMR Standard Deviation: 1225.7

		Percent | Themes
		------------ | -------------
		66% | fan,sci
		12% | adv,fan
		9% | adv,sci
		6% | sci,sup
		3% | mys,sci
		3% | adv,sup

		Percent | Cards
		------------ | -------------
		75% | Warboy Tweek
		72% | Visitors
		69% | Blood Elf Bebe
		59% | Terrance and Phillip
		56% | Poison
		53% | The Amazingly Randy
		53% | Paladin Butters
		47% | Le Bard Jimmy
		44% | Space Warrior Token
		41% | Princess Kenny
		41% | Catapult Timmy
		34% | Mecha Timmy
		34% | Bounty Hunter Kyle
		28% | Robo Bebe
		25% | Underpants Gnomes
		25% | Nathan
		22% | Dragonslayer Red
		19% | Mind Control
		16% | Satan
		16% | Program Stan
		16% | Medicine Woman Sharon
		16% | Kyle of the Drow Elves
		16% | Dogpoo
		12% | Cyborg Kenny
		9% | Witch Garrison
		9% | Smuggler Ike
		9% | Rat Swarm
		9% | Powerfist Dougie
		9% | Pirate Ship Timmy
		9% | Mr. Slave Executioner
		9% | Mintberry Crunch
		9% | Human Kite
		9% | Hookhand Clyde
		9% | Fireball
		9% | Enforcer Jimmy
		9% | Big Gay Al
		9% | Astronaut Butters
		9% | Arrowstorm
		6% | Towelie
		6% | Terrance Mephesto
		6% | Stan of Many Moons
		6% | Sharpshooter Shelly
		6% | Rogue Token
		6% | Professor Chaos
		6% | Pocahontas Randy
		6% | Mosquito
		6% | Lightning Bolt
		6% | Ice Sniper Wendy
		6% | Gunslinger Kyle
		6% | Grand Wizard Cartman
		6% | Doctor Timothy
		6% | Calamity Heidi
		6% | Alien Drone
		3% | Zen Cartman
		3% | Transmogrify
		3% | Toolshed
		3% | The Coon
		3% | Super Fart
		3% | Starvin' Marvin
		3% | Stan the Great
		3% | Sheriff Cartman
		3% | Robin Tweek
		3% | Prophet Dougie
		3% | Pope Timmy
		3% | Nelly
		3% | Marine Craig
		3% | Inuit Kenny
		3% | Elven King Bradley
		3% | Dwarf King Clyde
		3% | Dwarf Engineer Dougie
		3% | Cock Magic
		3% | Chiorboy Butters
		3% | Captain Wendy
		3% | Captain Diabetes
		3% | Canadian Knight Ike
		3% | Call Girl
		3% | Barrel Dougie
		3% | Bandita Sally
		3% | Alien Queen Red
		3% | Alien Clyde
		3% | A.W.E.S.O.M.-O 4000
		
	''',lang_index))

def PilgrimChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here's the Challenge Deck I used.
		
		Managed to go 12-1 and 12-0, getting a spot in the top 100.
		
		![Challenge Deck](https://i.imgur.com/QB4RZo5.png)
	
		Total Decks: 25, MMR Avg: 5427, MMR Standard Deviation: 2050.1

		Percent | Themes
		------------ | -------------
		32% | adv,fan
		20% | adv,sup
		16% | adv,sci
		16% | adv,neu
		12% | adv,mys
		4% | fan,sup

		Percent | Cards
		------------ | -------------
		72% | Pocahontas Randy
		72% | Medicine Woman Sharon
		68% | Stan of Many Moons
		68% | Calamity Heidi
		56% | Bandita Sally
		48% | Storyteller Jimmy
		44% | Lightning Bolt
		36% | Sheriff Cartman
		36% | Fireball
		36% | Dogpoo
		32% | Sharpshooter Shelly
		32% | Gunslinger Kyle
		28% | Blood Elf Bebe
		24% | Outlaw Tweek
		24% | Mosquito
		24% | Inuit Kenny
		24% | Human Kite
		24% | Dragonslayer Red
		24% | Big Mesquite Murph
		20% | Toolshed
		20% | Super Fart
		20% | Arrowstorm
		16% | Terrance and Phillip
		16% | Smuggler Ike
		16% | Shaman Token
		12% | Underpants Gnomes
		12% | Swordsman Garrison
		12% | Professor Chaos
		12% | Paladin Butters
		12% | Nathan
		12% | Incan Craig
		12% | Hookhand Clyde
		12% | Doctor Timothy
		8% | The Coon
		8% | Swashbuckler Red
		8% | Pigeon Gang
		8% | Mimsy
		8% | Energy Staff
		8% | Elven King Bradley
		8% | Dwarf Engineer Dougie
		8% | Deckhand Butters
		8% | Cyborg Kenny
		8% | Bounty Hunter Kyle
		8% | Big Gay Al
		8% | Astronaut Butters
		4% | Zen Cartman
		4% | Witch Garrison
		4% | Warboy Tweek
		4% | Visitors
		4% | Unholy Combustion
		4% | Towelie
		4% | The Amazingly Randy
		4% | Shieldmaiden Wendy
		4% | Santa Claus
		4% | Rogue Token
		4% | Robo Bebe
		4% | Rat Swarm
		4% | Program Stan
		4% | Princess Kenny
		4% | Power Bind
		4% | Pope Timmy
		4% | PC Principal
		4% | Nelly
		4% | Mysterion
		4% | Mind Control
		4% | Manbearpig
		4% | Ice Sniper Wendy
		4% | Hermes Kenny
		4% | Gizmo Ike
		4% | Chomper
		4% | Chiorboy Butters
		4% | Canadian Knight Ike
		4% | Call Girl
		4% | Barrel Dougie
		4% | Alien Queen Red
		4% | Alien Drone
		4% | Alien Clyde
		
	''',lang_index))

def ChristmasChallenge(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Managed to go 9-3 with an off-meta deck and 12-1 (1230 points) with this deck
		
		![Challenge Deck](https://i.imgur.com/3w3Oww3.png)
	
		Total Decks: 25, MMR Avg: 6204, MMR Standard Deviation: 1778.5

		Percent | Themes
		------------ | -------------
		36% | fan,mys
		16% | mys,sup
		16% | mys,sci
		16% | mys,neu
		8% | adv,mys
		4% | adv,sup
		4% | adv,sci

		Percent | Cards
		------------ | -------------
		84% | Pope Timmy
		76% | Priest Maxi
		76% | Chiorboy Butters
		72% | Sexy Nun Randy
		68% | The Master Ninjew
		52% | Mr. Hankey
		48% | Santa Claus
		40% | Unholy Combustion
		36% | Youth Pastor Craig
		36% | Jesus
		36% | Angel Wendy
		32% | Terrance and Phillip
		32% | Prophet Dougie
		32% | Friar Jimmy
		32% | Blood Elf Bebe
		24% | Hermes Kenny
		24% | Dragonslayer Red
		20% | Underpants Gnomes
		20% | Human Kite
		20% | Dogpoo
		16% | Zen Cartman
		16% | Energy Staff
		16% | Cupid Cartman
		12% | Visitors
		12% | Toolshed
		12% | Scout Ike
		12% | Power Bind
		8% | Stan of Many Moons
		8% | Nathan
		8% | Mosquito
		8% | Le Bard Jimmy
		8% | Hallelujah
		8% | Gizmo Ike
		8% | Enforcer Jimmy
		8% | Elven King Bradley
		8% | Captain Diabetes
		8% | Bounty Hunter Kyle
		4% | Witch Doctor Token
		4% | Warboy Tweek
		4% | Towelie
		4% | The Coon
		4% | The Amazingly Randy
		4% | Terrance Mephesto
		4% | Super Fart
		4% | Storyteller Jimmy
		4% | Space Warrior Token
		4% | Smuggler Ike
		4% | Shieldmaiden Wendy
		4% | Sharpshooter Shelly
		4% | Satan
		4% | Regeneration
		4% | Program Stan
		4% | Princess Kenny
		4% | Powerfist Dougie
		4% | Poseidon Stan
		4% | Pigeon Gang
		4% | Nelly
		4% | Mysterion
		4% | Mind Control
		4% | Mimsy
		4% | Medusa Bebe
		4% | Medicine Woman Sharon
		4% | Mecha Timmy
		4% | Marine Craig
		4% | Lightning Bolt
		4% | Hookhand Clyde
		4% | Gunslinger Kyle
		4% | Fireball
		4% | Fastpass
		4% | Dwarf King Clyde
		4% | Doctor Timothy
		4% | Deckhand Butters
		4% | Cyborg Kenny
		4% | Chomper
		4% | Call Girl
		4% | Astronaut Butters
		4% | Arrowstorm
		4% | Alien Drone
		
	''',lang_index))

def aboutPage(lang_index=0):
	return dcc.Markdown(HELPER.tr('''	
		**Welcome to the SPPDReplay Website**
		
		We are building off of the concepts for Hearthstone by HearthSim and their website [hsreplay.net](http://hsreplay.net)
		
		Our object is the same: Bring advanced gaming analytics and tools to the players
		
		We have this website, the [Deck Tracker](https://github.com/rbrasga/SPPD-Deck-Tracker), and the [Team Manager](https://github.com/rbrasga/SPPD-Team-Manager).
		
		Website Features:
		* Meta Deck Report - Themes & Cards
		   * Filterable by a range of options.
		   * Breakdown by Arena (From 0-300 up to 8500+)
		   * Updated every 24 hours.
		* Teams (Top 2000)
		   * Top 2000 Teams
		   * Filterable by a range of options.
		   * Best way to search for a new team.
		   * Updated each week.
		* All Players (on a Top 2000 Team)
		   * Every wondered if you have the most FF wins or challenge wins, or even donations?
		   * Updated every 24 hours.
		* Team Management
		   * Once you link your SPPD account, your team is auto-assigned.
		      * If it's not auto-assigned, then find your team and Click `REFRESH` under the Member's Tab
		   * Each player (or that player's team leader/co-leaders) can input card levels
		   * Team Wars Card Choices automatically updated when they become available
		      * Detailed Team Wars Caps Projections
			  * including Weighted Average Level (WAL) based on team's card levels
		* Custom Card Builder
		
		[Team Manager](https://github.com/rbrasga/SPPD-Team-Manager) Features:
		* Fully-Integrated with the website
		   * Run it on my cloud server for free with an optional recommended 2$ per month donation.
		      * [Sign up here](https://sppdreplay.net/teammanagercloud)
		   * OR on your own Windows PC. No setup, just download and run. Only Google Play email/password required.
		   * TVT Bracket Analytics
		      * Including email updates each time a score changes
		   * Track who spent caps where | who requested what | who donated what | weekend event points | teamwar history
		   * Auto-accept/reject team members based on white-list/black-list
		      * And auto-assign them their designated role

		[Deck Tracker](https://github.com/rbrasga/SPPD-Deck-Tracker) Features:
		   * Play like a pro! Keep track of the cards you and your opponent play with an in-game overlay.
		   * Keep track of the content you collect through lockers and packs
		   * (Optional) Automatically upload your data to the SPPDReplay website
		      * Uploaded Matches include opponent's true card levels, help with Challenge Meta Reports, and more.

		Pending Features:
		* SPPD Deck Tracker as a mobile application (no setup required) - including universal login (android <-> ios)
		* Eventually support optional upload for packs/lockers to support advanced analytics on epic/legendary drop rates for each pack type by tier
		* Deck builder

		**Join the [SPPD Replay Discord](https://discord.gg/j4Wchza) for more details.**
	''',lang_index))
	
def Downloads(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Download South Park Phone Destroyer™ - Battle Card Game
		   * [For Android](https://play.google.com/store/apps/details?id=com.ubisoft.dragonfire)
		   * [For iOS](https://apps.apple.com/us/app/south-park-phone-destroyer/id1106442030)
	
		Download the SPPD Deck Tracker
		   * [For PC](https://github.com/rbrasga/SPPD-Deck-Tracker)
			  * Log your matches/packs/lockers
		      * Link to your iOS or Android device
			  * Installation instructions are listed in the link.
	
		Download the Team Manager
		   * [For PC](https://github.com/rbrasga/SPPD-Team-Manager)
			  * Track Team War History, Upgrade Spending, Bracket Details
		      * Track Card Requests/Donations
		      * Track Team Event Participation
		      * Auto-Accept/Reject team members and assign roles
		      * Uploads data to this website for easy viewing anywhere.
			  * Installation instructions are listed in the link.
		   * Or for free with an optional recommended 2$ per month donation, I will host your team manager instance in the cloud, running non-stop. 
		      * [Sign up here](https://sppdreplay.net/teammanagercloud)
		
		[Join the discord](https://discord.gg/m95hg3S)!
		   * Help installing
		   * Answer questions
		   * Request features
		   * Report Bugs
			
	''',lang_index))
	
def DecksDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here are the meta decks built using an algorithm that finds the most paired card combinations by theme.
		
		* No one might be using this exact deck.
		* Best guess for what to expect if your opponent were running these theme combinations.
		* Strongly affected by challenge mode and card usage events, so check here daily.
		* Refreshed every day.
		
	''',lang_index))
	
def DeckbuilderDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here is deck builder using real-world data based on the win rate of themes and cards over 80k+ PVP matches.
		
		You can become a contributor by download the SPPD Deck Tracker and uploading your matches.
		
		* No one might be using this exact deck.
		* This data is from ALL Ranks at the moment.
		* Specific data sets will be coming in the future, so you can narrow down card win rate by Arena.
		
		How To Use:
		
		* To build your best deck, select your favorite theme or themes.
		* If you have one or more favorite cards, you can select those too.
		* If you want to specifically counter one or more cards or themes, select those in your opponent's deck.
		
	''',lang_index))
	
def CardsDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here are the meta cards by tier and time frame.
		
		* Depending on the time frame, the report may be affected by challenge mode or card usage events.
		* Filter by wide range of choices!
		* Refreshed every day.
		
	''',lang_index))
	
def AllCardsDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here are almost all of the cards in the game, including single player.
		
		* All data is updated frequently.
		
	''',lang_index))
	
def CompareCardsDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Compare 1 or more cards.
		
		* All data is updated frequently.
		
	''',lang_index))
	
def CardstatsDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here are the cards based on Damage Per Second (DPS).
		
		* Filter by Theme, Cost, Rarity, and Type.		
		* Credit for this data goes to `Da_Lemming#6110`
		
	''',lang_index))

def ThemesDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here are the meta theme combinations by tier and time frame.
		
		* Depending on the time frame, the report may be affected by challenge mode or card usage events.
		* Filter by wide range of choices!
		* Refreshed every day.
		
	''',lang_index))
	
def PlayersDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here is the player leader, including all active players on a top 2000 team.
		
		* Top 1000 Players Refreshed every day.
		* Others are Refreshed every month or so.
		* Search by name (must be 5 characters minimum)
		
	''',lang_index))
	
def TeamsDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here are (up to) the top 1000 global team leaderboard.
		
		* Looking for a new team? There's no better way to search.
		* Filter by wide range of choices!
		* Refreshed every day.
		
	''',lang_index))
	
def TeamwarsDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here is a breakdown of the TVT Deck Choices based on actual in-game data.
		
	''',lang_index))
	
def LiveMatchDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here are the most recent matches.
		
		* Matches uploaded using the SPPD Deck Tracker.
		* Filter by wide range of choices!
		   * Ranked OR Challenge Mode
		   * Specific Rank, like 8500+
		* Live! - See the matches as soon as they complete.
		
	''',lang_index))
	
def ChallengeDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here are the most recent Challenges (Chaos Mode).
		
		* Meta Report updated every hour if new matches were uploaded.
		
	''',lang_index))
	
def CollectionsDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here is your collection. You must input this information manually.
		
		* Linked to the SPPD account you set as your primary.
		* Allows your team to make better decisions about card levels during team wars.
		* Stored on every change (no need to click save)
		
	''',lang_index))
	
def MyMatchesDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Here are your matches.
		
		* The SPPD Deck Tracker can optionally upload your matches.
		* Your matches with other players are listed here, if they uploaded the match with the SPPD Deck Tracker.
		
	''',lang_index))
	
def SpecificTeamMembersTabDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
		
		Everyone can view Members
		
		Anyone can refresh Members once every 24 hours.
		
		All teams are auto-refreshed when Battle Days Ends.
		
	''',lang_index))
	
def SpecificTeamApplicationsTabDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
		
		Only Members can view.
		
		Only Leaders Can Set Accept/Reject and Roles.
		
		Team Manager App 1.x supports auto-accept/reject.
		
	''',lang_index))
	
def TWVoteDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
		
		Team Wars Card Choices are based on 
		
		* Card Levels of registered users with linked accounts who put their levels into the [My Cards Page](http://sppdreplay.ddns.net:8000/mycards).
		* Leaders/Co-Leaders can input their team members levels.
		
		Card Choices are auto-refreshed when Battle Days Ends.
		
	''',lang_index))
	
def TWBattleDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
		
		Team War Bracket Details
		
		If you want to see your bracket:
		
		* **Run the Team Manager App 24/7 in the CLOUD for free** with an optional recommended 2$ per month donation.
		   * [Sign up here](https://sppdreplay.net/teammanagercloud)
		* OR [Download](https://sppdreplay.net/downloads) the SPPD Team Manager App and run it on your own PC.
		
	''',lang_index))
	
def SpecificBracketDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
		
		Team War Bracket Details
		
		If you are signed in with an email address, you can subscribe to receive email updates on every change for one or more teams in this bracket.
		
	''',lang_index))
	
def CardRequestTabDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Card Requests Tab
		
		Only Team Members Can View
		
		Integrated with the Team Manager App
		
		Graph shows the top 10 most popular Card Requests over the last 2 weeks.
		
	''',lang_index))
	
def CardDonationTabDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Card Donations Tab
		
		Only Team Members Can View
		
		Integrated with the Team Manager App
		
	''',lang_index))
	
def BracketsDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
		
		At least one player on one team in a bracket is using the SPPD Team Manager App.
		
		If you want to see your bracket:
		
		* **Run the Team Manager App 24/7 in the CLOUD for free** with an optional recommended 2$ per month donation.
		   * [Sign up here](https://sppdreplay.net/teammanagercloud)
		* OR [Download](https://sppdreplay.net/downloads) the SPPD Team Manager App and run it on your own PC.
		
		Click the Bracket ID to see that specific bracket and subscribe for email updates.
		
	''',lang_index))
	
def TeamEventsDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Team Event Participation - Solo Packs Earned
		
		Event Types:
		* T - Locker Tokens
		* M - Mission
		* C - Card Usage
		
	''',lang_index))
	
def TeamWarHistoryDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Team War History Scores, by WEEK / YEAR
		
		Comments:
		* N/A - Not Applicable, They were not valid to play that week.
		* X - They were capable of playing, but DID NOT
		
	''',lang_index))
	
def TeamWarHistoryCapsDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Team War History Caps, by WEEK / YEAR
		
	''',lang_index))
	
def DonateDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
	
		Thank you for using my website. I originally designed this project to make my life easier, but I'm happy to see that it makes other people's lives easier as well.
		
		All these services (website) and apps (Deck Tracker, Team Manager) were written by me, in my free time...
		Occasionally with a sleeping baby strapped to my chest.
		
		I work full-time supporting my wife and three boys. Here's a picture of Me and My Boys:
		
		![Me and My Boys](https://i.imgur.com/Kq0M6Oj.jpg)
		
		
		I pay for everything out of my own pocket. And I feel that it would be really nice if some of you guys could help a father out with some donations, so that my hobby could finally stop taking money out of my pocket.
		
		If your team uses my services, please consider a $1.00 donation per month.
		OR donate 1$ per month to your favorite charity and share the receipt with me on the [SPPD Replay Discord](https://discord.gg/j4Wchza).
		
		My goal for this project was to improve the community by bringing everyone together, not to make a fortune.
		
		Sincerely,
		-Remington
		
		Bitcoin: `199bUXG64uSrGwBiY6xgizzU8VZWCfGJ5f`
		![Bitcoin Address](https://i.imgur.com/Nn3LV8H.png)
	''',lang_index))
	
def GettingStartedDescription(lang_index=0):
	return dcc.Markdown(HELPER.tr('''

**Step 1** - Register

  * Click [Login](https://sppdreplay.net/login)
  * On the OKTA Sign-in Page, click **Sign Up**.
  * Register with a real email if you want to subscribe to Live Bracket Email Updates
    - Or with a fake email address, just don't forget your website login.
		
**Step 2** - Link Your Account

  * Go to your [Settings](https://sppdreplay.net/settings)

  * Add Your Tracking ID. The website already has 99% of all Tracking IDs, you just need to say which one is yours.

  * **How do I find my TRACKING ID?**

  1. Go to SPPD's In-Game Settings

  ![Settings](https://i.imgur.com/IL2VXGQ.png)

  2. Scroll to the bottom

  ![Tracking ID](https://i.imgur.com/zxeD4NS.png)

  * Notes:
    - Each Tracking ID can only be claimed once. So don't forget your website login.
    - Each website login can claim up to three SPPD accounts.
      - Or ten SPPD accounts for a small donation to me or your favorite charity.
    - If you want to Opt-Out of having your levels be public, Click `Opt-Out`.
      - If you opt-out, only your team members will be able to view your card levels if they are logged in.
	
**Step 3** - Input your card levels
	
  * Hover over or Click `My Data`
  * Click [My Cards](https://sppdreplay.net/mycards)
  * Plug in your card levels.

  * You may see yourself or your team members with a dozen or more card levels already because of data from matches uploaded through SPPD [Deck Tracker](https://sppdreplay.net/downloads)
	
**Step 4** - Enjoy.

  * Check out your team page while logged in.
  * If someone on your team is running the SPPD [Team Manager App](https://sppdreplay.net/downloads) you can track everything team-related.
	
If you have any questions: [Join the discord](https://discord.gg/m95hg3S)!

	''',lang_index))
	
def CustomDeckDetails(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
Custom Deck for Friendly Fights

**Step 1** - Check if the stream is live.

  * Only while my [twitch stream](https://www.twitch.tv/sparkpcmr) is live, I will host a proxy server that enables this feature - my own personal Deck Tracker.
		
**Step 2** - Install the certificate on your android/iOS device
  * This step is only needed once. And NOT needed if you already setup the SPPD [Deck Tracker](https://sppdreplay.net/downloads).

  * I think only Android Emulators like Nox will work.
  * All iOS devices work.
  
  * On your device, download and install the certificate at https://sppdreplay.net:8888
  
  * If you are using iOS, you must search in settings for "Certificate Trust Settings", and enable full trust for root certificate.
  * If you are using Android, you must set a password.

	
**Step 3** - Set the proxy
	
  * For iOS devices, you must be connected to Wifi (4G doesn't let you set a proxy)
  * Set the Proxy to
     * HOST: sppdreplay.net
	 * PORT: 8888
	
**Step 4** - Enjoy.

  * Launch South Park Phone Destroyer
  * Open the **EASTER EGG** free pack
     * you don't get to keep these cards
  * Optional: Try on some outfits you don't own yet
     * you don't get to keep the outfits
  * Join the team: **CustomDeck**
     * I will kick everyone when the stream ends
  * Queue for a friendly fight!
     * Play me, and your match will be streamed on Twitch: https://www.twitch.tv/sparkpcmr
  * NOTE: After I take down my proxy and you restart your game, it will be as if nothing happened.
  
**Step 5** - Clean up.
  * Remove the proxy.
	

If you have any questions: [Join the discord](https://discord.gg/m95hg3S)!
	''',lang_index))
	
def PrivacyPolicy(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
**Privacy Policy**

**What information is collected?**

  * SPPD Replay
    * When you log in to this website, you are welcome to use any email address (whether or not that email address actually exists). We will never share your name or email address.
	* SPPD Replay collects publicly available data from the game SPPD (South Park Phone Destroyer), and stores it for later analysis
	* You can "link" your account, which just means providing your in-game tracking ID. All this does is tell SPPD Replay which of the 200,000 accounts is yours. No one would know whether or not you have linked your account.
  * SPPD Team Manager App
    * Collects data that is private to a team, such as that team's Team War Bracket data, or how members of that team earn/spend their upgrade caps.
	* Although the team manager cloud does require your Google Play Games user name and password, only the user name and SPPD-related token, generated by the open source SPPD API, are stored.
  * SPPD Chat Bot
    * The channel ID and webhook details for a discord channel are stored for continuous synchronization across service restarts.
    * Collects - but DOES NOT STORE - messages from a team's in-game chat and a discord channel, so as to synchronize the channel.
	* In-game chat automatically erases the entire message history every 1 week or less.
	* In-game messages would be "stored" on the discord channel for which the chat bot is synchronized to.
  * Douglas
    * The User ID of the user who creates a custom bind is stored to prevent abuse
	* Otherwise douglas does not track any messages or users.

**Where information is collected from?**

  * SPPD Replay collects publicly available data from the game SPPD (South Park Phone Destroyer), and stores it for later analysis
  * The SPPD Team Manager app provides data for a team and all of its members for better team war data tracking and analysis.

**Why information is collected?**

  * Your email address may be used if you subscribe for bracket updates over email.

**How information is collected (including through cookies and other tracking technologies)?**

  * I do use Google Analytics. Otherwise I don't do any cookie tracking of my own, or use any other technologies.

**Who information is shared with or sold to?**

  * I don't sell any information.

**What rights users have over their data?**

  * You are welcome to link your account and "opt-out", meaning no one will be able to view your profile page, which includes your skill point history, past names, and past teams, etc.

**The site’s contact details**

  * Reach out to me on the [SPPD Replay Discord](https://discord.gg/j4Wchza)
  * Or file an issue on an SPPD-related github project: https://github.com/rbrasga/


	''',lang_index))
	
def BannedUpdate(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
**BANNED UPDATE**

Hey Everyone, 

An update on the situation for those interested.

In short:

* Ban appears permanent even though I believe I did not break the terms of service.
* Website will remain online.
* Exploits still exist.

**BANNED**

I won't be playing until the communication between the game and the community improves from the fake "I'm sorry / Oops, I forgot". Because any sane community leader would clearly reverse my ban, we have to assume they just want to have the appearance of working hard (and yes, server side is on the way 100%). I also won't sink to Redlynx level or help them destroy their community by bringing down the SPPD Replay website/services, because they are doing that on their own.

I believe I didn't break the rules of conduct for which I was banned, though no one at redlynx will tell me which rule was broken. They also updated their Terms of Service in May 2020 and removed any references to "reverse engineering", probably because someone enjoyed people like me contributing positively to their games.

Here's the only rules that I see that could apply to my situation [https://legal.ubi.com/termsofuse/en-US](https://legal.ubi.com/termsofuse/en-US):

* Engage in any activity, such as cheating, hacking, botting, boosting, or tampering that gives the Account owner (and/or his/her teammate(s)) an unfair advantage or causes detriment to other players’ experience
* Exploit of any new or known glitches/bugs which provide an unfair advantage over other players
* Refuse to obey the instructions of any UBISOFT representatives.

As I was playing friendly fights, which give no rewards or points of any kind and can only be done between people on the same team, the point cannot be made that I had an unfair advantage or caused a detriment to other players' experience.

As for the last rule I noted - I reached out to Toller, the SPPD Community Manager, requesting if it was allowed to play friendly fights in the way I did, and I have still never gotten a response to those messages. So the case can be made that I always obeyed the instructions of an UBISOFT representative.

**EXPLOITS**

There are currently exploits in this game that allow a user to have any card level they want in any game mode (PVP/Challenge/TVT/PVE). On top of that, a user can also make their units invincible (or your units only deal 1% to 99% damage to be more subtle). Among other lesser exploits, like custom deck friendly fights (which should honestly be a feature available to everyone).

All of this can be done quite easily AND it's undetectable (no automatic ban for these exploits) and you can be sure I won't be the first person to find these exploits. However, I want the time and/or money you spent on this game to mean something - so yet again I'm willing to be the better man and work with Redlynx to resolve these issues, whether they unban me or not.

Don't worry, I'm not about to release a Toolbox 2.0 like Hydeen. It was fun working together even if we were always like Yin and Yang. I'm just hoping Redlynx can actually fix their game rather than manually banning the 1 in 100 players that someone managed to get a screenshot of.

**CONCLUSION**

This is fight club. Don't spread this information on reddit or the official SPPD discord. Keep it to yourself.

Sincerely,
-Remington
	''',lang_index))
	
def invalidArticle(lang_index=0):
	return dcc.Markdown(HELPER.tr('''
		Oops. This article doesn't exist!
	''',lang_index))
	
ARTICLES_DICT={
	"Privacy Policy" : [29, PrivacyPolicy],
	"12/15 Banned Update" : [28, BannedUpdate],
	"Custom Deck Friendly Fights" : [27, CustomDeckDetails],
	"08/05 Elves vs Aliens Challenge" : [26, ElvesAliensChallenge],
	"Getting Started" : [25, GettingStartedDescription],
	"07/08 The Dark Angel's Gift Challenge" : [24, DarkAngelChallenge],
	"06/30 SPPD Known Issues)" : [23, KnownIssues],
	"06/17 Whimpy Kid Challenge)" : [22, WhimpyKidChallenge],
	"06/10 Space Pilots Challenge)" : [21, SpacePilotsChallenge],
	"06/03 Candy Destroyer Challenge)" : [20, CandyDestroyerChallenge],
	"05/27 Speed Chaser Kyle Challenge)" : [19, SpeedChaserKyleChallenge],
	"05/20 Furry Beasts Challenge)" : [18, FurryBeastsChallenge],
	"05/13 Ultra Speed Crew Challenge)" : [17, UltraSpeedCrewChallenge],
	"05/06 Spellbenders Challenge)" : [16, SpellbendersChallenge2],
	"04/29 Chaos Challenge)" : [15, ChaosChallenge],
	"04/22 Neutral Challenge)" : [14, NeutralChallenge],
	"04/15 Inanimate Challenge)" : [13, InanimateChallenge],
	"04/08 Big Boy Challenge)" : [12, BigBoyChallenge],
	"03/18 The Commoners Challenge)" : [11, CommonChallenge],
	"03/11 Wheel of Fortune Challenge)" : [10, WheelOfFortuneChallenge],
	"03/04 Pilgrim Challenge (again)" : [9, PilgrimChallenge2],
	"02/19 Super Craig & Wonder Tweek Challenge" : [8, CraigTweekChallenge],
	"02/05 2019 Wrap-Up Challenge" : [7, WrapUp2019Challenge],
	"01/29 Electric Challenge" : [6, ElectricChallenge],
	"01/08 Spellbenders Challenge" : [5, SpellbendersChallenge],
	"12/25 Christmas Challenge" : [4, ChristmasChallenge],
	"12/04 Rangers Challenge" : [3, RangersChallenge],
	"11/27 Pilgrim Challenge" : [2, PilgrimChallenge],
	"About" : [0, aboutPage],
}