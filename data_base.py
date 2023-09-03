import sqlite3 as sq
import json
from random import randint, choice
from create_bot import MAKEUPS, MAKEUPS_WO_LIPS


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
                    colours TEXT,
                    collections TEXT,
                    priority INTEGER
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

        base.execute('''CREATE TABLE IF NOT EXISTS images(
                                                           id INTEGER PRIMARY KEY,
                                                           user_id INTEGER,
                                                           telegram_id INTEGER,
                                                           name TEXT
                                                           )''')

    base.commit()


def get_elements(user_id, element):
    cur.execute('SELECT name, id, collection FROM makeup_elements WHERE user_id = ? AND type = ?',
                (user_id, element))
    elements = cur.fetchall()
    return elements


def get_one_element(user_id, element_id):
    cur.execute('SELECT name, type, colours, collection, priority FROM makeup_elements WHERE user_id = ? AND id = ?',
                (user_id, element_id))
    element = cur.fetchone()
    ret = {'name': element[0],
           'type': element[1],
           'id': element_id,
           'colours': '',
           'collection': element[3],
           'priority': element[4]}
    colours = json.loads(element[2])
    for colour_id in colours:
        cur.execute('SELECT name FROM colours WHERE id = ?',
                    (colour_id,))
        colour_name = cur.fetchone()[0]
        ret['colours'] = '/'.join((ret['colours'], colour_name)) if ret['colours'] else colour_name

    return ret


def get_readable_elements(user_id, element):
    cur.execute('SELECT name, colours, collection, priority FROM makeup_elements WHERE user_id = ? AND type = ?',
                (user_id, element))
    elements = cur.fetchall()
    ret_elements = []
    for element in elements:
        ret_elements.append([f'{element[0].capitalize()} ({element[2]})' if element[2] else element[0].capitalize()])
        colours = json.loads(element[1])
        ret_elements[-1].append('')
        ret_elements[-1].append(element[3])
        for colour_id in colours:
            cur.execute('SELECT name FROM colours WHERE id = ?',
                        (colour_id,))
            colour_name = cur.fetchone()[0]
            ret_elements[-1][1] = ', '.join((ret_elements[-1][1], colour_name)) if ret_elements[-1][1] else colour_name

    return ret_elements


def add_element(user_id, name, mk_type, colours, collection):
    colours = json.dumps(colours)
    cur.execute('INSERT INTO makeup_elements VALUES(null, ?, ?, ?, ?, ?, 6)',
                (user_id, mk_type, name, colours, collection))
    # cur.execute('INSERT INTO makeup_elements(user_id, type, name, colours) VALUES(?, ?, ?, ?)', (user_id, mk_type, name, colours))
    base.commit()


def remove_element(user_id, element_id):
    cur.execute('''DELETE FROM makeup_elements WHERE user_id = ? AND id = ?''',
                (user_id, element_id))
    base.commit()


def get_colours(user_id):
    cur.execute('SELECT name, id FROM colours WHERE user_id = ?',
                (user_id,))
    colours = cur.fetchall()
    colours = sorted(colours, key=lambda colour: colour[0])
    return colours


def add_colour(user_id, colour_name):
    cur.execute('INSERT INTO colours VALUES(null, ?, ?)',
                (user_id, colour_name))
    base.commit()


def remove_colour(user_id, colour_id):
    cur.execute('''DELETE FROM colours WHERE user_id = ? AND id = ?''',
                (user_id, colour_id))
    base.commit()


def get_colour_stories(user_id):
    cur.execute('SELECT name, id FROM colour_stories WHERE user_id = ?',
                (user_id,))
    colour_stories = cur.fetchall()
    return colour_stories


def add_colour_story(user_id, colours):
    name = '/'.join((str(col[0]) for col in colours))
    colours = json.dumps([col[1] for col in colours])
    cur.execute('INSERT INTO colour_stories VALUES(null, ?, ?, ?)',
                (user_id, name, colours))
    base.commit()


def remove_colour_story(user_id, cs_id):
    cur.execute('''DELETE FROM colour_story WHERE user_id = ? AND id = ?''',
                (user_id, cs_id))
    base.commit()


def get_elements_by_priority(elements):
    # input data: ((name, colours, priority, collection), ...)

    if not elements:
        return elements
    weights = []
    for el in elements:
        if el[2] not in weights:
            weights.append(el[2])

    new_elements = []
    while not new_elements:
        cur_weight = max(weights)
        dice = randint(1, 10)
        if dice <= cur_weight:
            for el in elements:
                if el[2] == cur_weight:
                    new_elements.append(el)
        else:
            weights.remove(cur_weight)
            if not weights:
                new_elements.append(choice(elements))
    return new_elements


def get_makeup_from_colour_story(user_id, colour_story_id):
    makeup = {}
    cur.execute('SELECT colours FROM colour_stories WHERE user_id = ? AND id = ?',
                (user_id, colour_story_id))
    colours = json.loads(cur.fetchone()[0])

    for element_type in MAKEUPS_WO_LIPS:
        if element_type == 'eyeliner' and randint(0, 1):
            makeup[element_type] = 'Black'
            continue

        if element_type == 'glitter' and randint(0, 1):
            makeup[element_type] = 'Use NO glitter'
            continue

        cur.execute('SELECT name, colours, priority, collection FROM makeup_elements WHERE user_id = ? AND type = ?',
                    (user_id, element_type))
        all_elements = cur.fetchall()
        elements_to_use = []
        for current_element in all_elements:
            for colour in json.loads(current_element[1]):
                if colour in colours:
                    elements_to_use.append(current_element)
                    break

        elements_to_use = get_elements_by_priority(elements_to_use)

        if elements_to_use:
            if element_type == 'eyeshadow' or element_type == 'eyeliner':
                amount = randint(1, 3)
                makeup[element_type] = ''
                if len(elements_to_use) < amount:
                    makeup[element_type] = ', '.join([f'{i[0]} ({i[3]})' if i[3] else i[0]
                                                      for i in elements_to_use])
                else:
                    for i in range(amount):
                        curr_makeup = choice(elements_to_use)
                        elements_to_use.remove(curr_makeup)
                        curr_makeup_text = f'{curr_makeup[0]} ({curr_makeup[3]})' if curr_makeup[3] else curr_makeup[0]
                        makeup[element_type] = (', '.join((makeup[element_type], curr_makeup_text))
                                                if makeup[element_type] else curr_makeup_text)
            else:
                curr_makeup = choice(elements_to_use)
                curr_makeup_text = f'{curr_makeup[0]} ({curr_makeup[3]})' if curr_makeup[3] else curr_makeup[0]
                makeup[element_type] = curr_makeup_text
        else:
            if element_type == 'glitter':
                makeup[element_type] = 'Use NO glitter'
            else:
                makeup[element_type] = f'No <b>{element_type}</b> in database!'

    return makeup

    # return {'eyeshadow': 'some eyeshadow',
    #         'eyeliner': 'some eyeliner',
    #         'lipstick': 'some lipstick',
    #         'lipliner': 'some lipliner',
    #         'lipgloss': 'some lipgloss',
    #         'highlighter': 'some ---',
    #         'blush': 'some ---',
    #         'glitter': 'some ---',
    #         'mascara': 'some ---'}


def get_full_random(user_id):
    makeup = {}

    for element_type in MAKEUPS:
        if element_type == 'eyeliner' and randint(0, 1):
            makeup[element_type] = 'Black'
            continue

        if element_type == 'glitter' and randint(0, 1):
            makeup[element_type] = 'Use NO glitter'
            continue

        cur.execute('SELECT name, collection FROM makeup_elements WHERE user_id = ? AND type = ?',
                    (user_id, element_type))
        all_elements = list(cur.fetchall())
        if all_elements:
            if element_type == 'eyeshadow' or element_type == 'eyeliner':
                amount = randint(1, 3)
                makeup[element_type] = ''
                if len(all_elements) < amount:
                    makeup[element_type] = ', '.join([f'{i[0]} ({i[1]})' if i[1] else i[0]
                                                      for i in all_elements])
                else:
                    for i in range(amount):
                        curr_makeup = choice(all_elements)
                        all_elements.remove(curr_makeup)
                        curr_makeup_text = f'{curr_makeup[0]} ({curr_makeup[1]})' if curr_makeup[1] else curr_makeup[0]
                        makeup[element_type] = (', '.join((makeup[element_type], curr_makeup_text))
                                                if makeup[element_type] else curr_makeup_text)
            else:
                curr_makeup = choice(all_elements)
                curr_makeup_text = f'{curr_makeup[0]} ({curr_makeup[1]})' if curr_makeup[1] else curr_makeup[0]
                makeup[element_type] = curr_makeup_text
        else:
            if element_type == 'glitter':
                makeup[element_type] = 'Use NO glitter'
            else:
                makeup[element_type] = f'No <b>{element_type}</b> in database!'

    return makeup


def find(user_id, mk_type, name):
    cur.execute('SELECT name, id, collection FROM makeup_elements WHERE user_id = ? AND type = ?',
                (user_id, mk_type))
    elements = cur.fetchall()
    result = []
    for elem in elements:
        if name in elem[0]:
            result.append(elem)

    return result


def edit(mk_id, field, new_value):
    cur.execute(f'UPDATE makeup_elements SET {field} = ? WHERE id = ?',
                (new_value, mk_id))
    base.commit()


def find_existence(user_id, full_name):
    if '(' in full_name and ')' in full_name:
        collection = full_name[full_name.index('(') + 1:full_name.index(')')]
        name = full_name[:full_name.index('(')]
        if name[-1] == ' ':
            name = name[:-1]
    else:
        name = full_name
        collection = None
    cur.execute('SELECT id FROM makeup_elements WHERE user_id = ? AND name = ? AND collection = ?',
                (user_id, name, collection))
    if cur.fetchone():
        return True
    else:
        return False


def add_image(user_id, name, telegram_id):
    cur.execute('''INSERT INTO images (user_id, name, telegram_id)
            VALUES(?, ?, ?)''', (user_id, name, telegram_id))
    base.commit()


def get_random_image(user_id):
    cur.execute('SELECT id, name, telegram_id FROM images WHERE user_id = ?',
                (user_id,))

    images = cur.fetchall()
    if images:
        image = choice(images)
        return {'id': image[0],
                'name': image[1],
                'telegram_id': image[2]
                }
    else:
        return None


def get_all_images_names(user_id, ):
    cur.execute('SELECT id, name FROM images WHERE user_id = ?',
                (user_id,))
    return cur.fetchall()


def remove_image(image_id):
    cur.execute('''DELETE FROM images WHERE id = ?''',
                (image_id,))
    base.commit()


def image_find_existence(user_id, name):
    cur.execute('SELECT id FROM images WHERE user_id = ? AND name = ?',
                (user_id, name))
    if cur.fetchone():
        return True
    else:
        return False


def get_pallets(user_id):
    cur.execute('SELECT DISTINCT collection FROM makeup_elements WHERE user_id = ?',
                (user_id,))
    return cur.fetchall()


def change_pallet_priority(user_id, pallet_name, new_priority):
    cur.execute(f'UPDATE makeup_elements SET priority = ? WHERE user_id = ? AND collection = ?',
                (new_priority, user_id, pallet_name))
    base.commit()


def eyeshadowing(user_id, eyeshadow_id):
    cur.execute('SELECT name, colours, collection from makeup_elements WHERE id = ?',
                (eyeshadow_id,))
    raw_eyeshadow = cur.fetchone()
    eyeshadow = {'name': raw_eyeshadow[0],
                 'colours': json.loads(raw_eyeshadow[1]),
                 'collection': raw_eyeshadow[2]}

    cur.execute('SELECT id, name, colours FROM colour_stories WHERE user_id = ?',
                (user_id,))
    raw_colour_stories = cur.fetchall()
    accepted_colour_stories = []
    for cs in raw_colour_stories:
        for colour in eyeshadow['colours']:
            if colour in json.loads(cs[2]):
                accepted_colour_stories.append(cs)
                break
    if not accepted_colour_stories:
        return f'No accepted colour stories for {eyeshadow["name"]} ({eyeshadow["collection"]})!'

    colour_story = choice(accepted_colour_stories)
    makeup = get_makeup_from_colour_story(user_id, colour_story[0])

    new_eyeshadows = makeup['eyeshadow'].split(', ')
    print(new_eyeshadows)
    if f'{eyeshadow["name"]} ({eyeshadow["collection"]})' not in new_eyeshadows:
        new_eyeshadows[0] = f'{eyeshadow["name"]} ({eyeshadow["collection"]})'
        makeup['eyeshadow'] = ', '.join(new_eyeshadows)

    elements_text = '\n'.join(f'{mkp.capitalize()}: <b>{makeup[mkp]}</b>' for mkp in MAKEUPS_WO_LIPS)

    text = '\n'.join((f'Eyeshadowing by {eyeshadow["name"]} ({eyeshadow["collection"]})',
                      f'Colour story: <i>{colour_story[1]}</i>',
                      elements_text))

    return text
