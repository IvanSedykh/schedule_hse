import json
from icalendar import Calendar, Event, vText
import codecs

def parse_ics(ics):
    events = []
    with codecs.open(ics, 'r', 'utf-8') as rf:
        ical = Calendar().from_ical(rf.read())
        ical_config = dict(ical.sorted_items())
        for i, comp in enumerate(ical.walk()):
            if comp.name == 'VEVENT':
                event = {}
                for name, prop in comp.property_items():

                    if name in ['SUMMARY', 'LOCATION']:
                        event[name.lower()] = prop.to_ical().decode('utf-8')

                    elif name == 'DTSTART':
                        event['start'] = {
                            'dateTime': prop.dt.isoformat(),
                            'timeZone': 'Europe/Moscow' #str(prop.dt.tzinfo)
                        }

                    elif name == 'DTEND':
                        event['end'] = {
                            'dateTime': prop.dt.isoformat(),
                            'timeZone': 'Europe/Moscow' #str(prop.dt.tzinfo)
                        }

                    elif name == 'SEQUENCE':
                        event[name.lower()] = prop

                    elif name == 'TRANSP':
                        event['transparency'] = prop.lower()

                    elif name == 'CLASS':
                        event['visibility'] = prop.lower()

                    elif name == 'ORGANIZER':
                        event['organizer'] = {
                            'displayName': prop.params.get('CN') or '',
                            'email': re.match('mailto:(.*)', prop).group(1) or ''
                        }

                    elif name == 'DESCRIPTION':
                        desc = prop.to_ical().decode('utf-8')
                        desc = desc.replace(u'\xa0', u' ')
                        if name.lower() in event:
                            event[name.lower()] = desc + '\r\n' + event[name.lower()]
                        else:
                            event[name.lower()] = desc

                    elif name == 'X-ALT-DESC' and 'description' not in event:
                        soup = BeautifulSoup(prop, 'lxml')
                        desc = soup.body.text.replace(u'\xa0', u' ')
                        if 'description' in event:
                            event['description'] += '\r\n' + desc
                        else:
                            event['description'] = desc

                    elif name == 'ATTENDEE':
                        if 'attendees' not in event:
                            event['attendees'] = []
                        RSVP = prop.params.get('RSVP') or ''
                        RSVP = 'RSVP={}'.format('TRUE:{}'.format(prop) if RSVP == 'TRUE' else RSVP)
                        ROLE = prop.params.get('ROLE') or ''
                        event['attendees'].append({
                            'displayName': prop.params.get('CN') or '',
                            'email': re.match('mailto:(.*)', prop).group(1) or '',
                            'comment': ROLE
                            # 'comment': '{};{}'.format(RSVP, ROLE)
                        })

                    # VALARM: only remind by UI popup
                    elif name == 'ACTION':
                        event['reminders'] = {'useDefault': True}

                    else:
                        # print(name)
                        pass

                events.append(event)

    return events

def convert (fname=None):
	result = parse_ics(fname)
	return result
