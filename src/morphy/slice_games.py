import sys
sys.path.insert(0, '/Users/majki/Projects/morphy/src')

from morphy.utils import games_reader


def main(first_game, games_number):
    pgn = open("/Users/majki/Projects/morphy_data/caissabase.pgn", 'r')
    counter = 1

    for g in games_reader(pgn):
        
        if counter < first_game:
            continue
        counter += 1

        if not games_number:
            break
            
        games_number -= 1
        
        print(g)

    

if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]))
