import sqlite3 as sq
import json
from random import randint, choice
from create_bot import MAKEUPS


def sqlStart():
    global base, cur
    base = sq.connect('makeup.db')
    cur = base.cursor()
    if base:
        print('Data base connected.')

        base.execute('''CREATE TABLE IF NOT EXISTS makeup_elements(
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    type TEXT,
                    name TEXT,
                    colours TEXT
                    )''')

        base.execute('''CREATE TABLE IF NOT EXISTS colours(
                                            id INTEGER PRIMARY KEY,
                                            user_id INTEGER,
                                            name TEXT
                                            )''')

        base.execute('''CREATE TABLE IF NOT EXISTS colour_stories(
                                                    id INTEGER PRIMARY KEY,
                                                    user_id INTEGER,
                                                    name TEXT,
                                                    colours TEXT
                                                    )''')

    base.commit()


def get_elements(user_id, element):
    cur.execute('SELECT name, id FROM makeup_elements WHERE user_id = ? AND type = ?', (user_id, element))
    elements = cur.fetchall()
    return elements


def get_readable_elements(user_id, element):
    cur.execute('SELECT name, colours FROM makeup_elements WHERE user_id = ? AND type = ?', (user_id, element))
    elements = cur.fetchall()
    ret_elements = []
    for element in elements:
        ret_elements.append([element[0].capitalize()])
        colours = json.loads(element[1])
        ret_elements[-1].append('')
        for colour_id in colours:
            cur.execute('SELECT name FROM colours WHERE id = ?', (colour_id,))
            colour_name = cur.fetchone()[0]
            ret_elements[-1][1] = ', '.join((ret_elements[-1][1], colour_name)) if ret_elements[-1][1] else colour_name

    return ret_elements


def add_element(user_id, name, mk_type, colours):
    colours = json.dumps(colours)
    cur.execute('INSERT INTO makeup_elements VALUES(null, ?, ?, ?, ?)', (user_id, mk_type, name, colours))
    # cur.execute('INSERT INTO makeup_elements(user_id, type, name, colours) VALUES(?, ?, ?, ?)', (user_id, mk_type, name, colours))
    base.commit()


def remove_element(user_id, element_id):
    cur.execute('''DELETE FROM makeup_elements WHERE user_id = ? AND id = ?''', (user_id, element_id))
    base.commit()


def get_colours(user_id):
    cur.execute('SELECT name, id FROM colours WHERE user_id = ?', (user_id,))
    colours = cur.fetchall()
    return colours


def add_colour(user_id, colour_name):
    cur.execute('INSERT INTO colours VALUES(null, ?, ?)', (user_id, colour_name))
    base.commit()


def remove_colour(user_id, colour_id):
    cur.execute('''DELETE FROM colours WHERE user_id = ? AND id = ?''', (user_id, colour_id))
    base.commit()


def get_colour_stories(user_id):
    cur.execute('SELECT name, id FROM colour_stories WHERE user_id = ?', (user_id,))
    colour_stories = cur.fetchall()
    return colour_stories


def add_colour_story(user_id, colours):
    name = '/'.join((str(col[0]) for col in colours))
    colours = json.dumps([col[1] for col in colours])
    cur.execute('INSERT INTO colour_stories VALUES(null, ?, ?, ?)', (user_id, name, colours))
    base.commit()


def remove_colour_story(user_id, cs_id):
    cur.execute('''DELETE FROM colour_story WHERE user_id = ? AND id = ?''', (user_id, cs_id))
    base.commit()


def get_makeup_from_colour_story(user_id, colour_story_id):
    makeup = {}
    cur.execute('SELECT colours FROM colour_stories WHERE user_id = ? AND id = ?', (user_id, colour_story_id))
    colours = json.loads(cur.fetchone()[0])

    for element_type in MAKEUPS:
        if element_type == 'eyeliner' and randint(0, 1):
            makeup[element_type] = 'Black'
            continue

        cur.execute('SELECT name, colours FROM makeup_elements WHERE user_id = ? AND type = ?', (user_id, element_type))
        all_elements = cur.fetchall()
        elements_to_use = []
        for current_element in all_elements:
            for colour in json.loads(current_element[1]):
                if colour in colours:
                    elements_to_use.append(current_element[0])
                    break

        if elements_to_use:
            if element_type == 'eyeshadow' or element_type == 'eyeliner':
                amount = randint(1, 3)
                makeup[element_type] = ''
                if len(elements_to_use) < amount:
                    makeup[element_type] = ', '.join([i for i in elements_to_use])
                else:
                    for i in range(amount):
                        curr_makeup = choice(elements_to_use)
                        elements_to_use.remove(curr_makeup)
                        makeup[element_type] = ', '.join((makeup[element_type],
                                                          curr_makeup)) if makeup[element_type] else curr_makeup
            else:
                makeup[element_type] = choice(elements_to_use)
        else:
            makeup[element_type] = f'No <b>{element_type}</b> in database!'

    makeup['glitter'] = bool(randint(0, 1))
    return makeup

    # return {'eyeshadow': 'some eyeshadow',
    #         'eyeliner': 'some eyeliner',
    #         'lipstick': 'some lipstick',
    #         'lipliner': 'some lipliner',
    #         'lipgloss': 'some lipgloss',
    #         'highlighter': 'some ---',
    #         'blush': 'some ---',
    #         'glitter': True}


def get_full_random(user_id):
    makeup = {}

    for element_type in MAKEUPS:
        if element_type == 'eyeliner' and randint(0, 1):
            makeup[element_type] = 'Black'
            continue

        cur.execute('SELECT name FROM makeup_elements WHERE user_id = ? AND type = ?', (user_id, element_type))
        all_elements = list(cur.fetchall())
        if all_elements:
            if element_type == 'eyeshadow' or element_type == 'eyeliner':
                amount = randint(1, 3)
                makeup[element_type] = ''
                if len(all_elements) < amount:
                    makeup[element_type] = ', '.join([i for i in all_elements])
                else:
                    for i in range(amount):
                        curr_makeup = choice(all_elements)
                        all_elements.remove(curr_makeup)
                        makeup[element_type] = ', '.join((makeup[element_type],
                                                          curr_makeup[0])) if makeup[element_type] else curr_makeup[0]
            else:
                makeup[element_type] = choice(all_elements)[0]
        else:
            makeup[element_type] = f'No <b>{element_type}</b> in database!'

    makeup['glitter'] = bool(randint(0, 1))
    return makeup


def find(user_id, mk_type, name):
    cur.execute('SELECT name, id FROM makeup_elements WHERE user_id = ? AND type = ?',
                (user_id, mk_type))
    elements = cur.fetchall()
    result = []
    for elem in elements:
        if name in elem[0]:
            result.append(elem)

    return result

