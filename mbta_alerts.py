import json
import sys, re, os, subprocess
import argparse
from datetime import datetime

API_KEY = "c494da3065604abb9888dda3c074f6a3"
API_URL = "https://api-v3.mbta.com/predictions/?filter\\[route\\]={route}&filter\\[stop\\]=place-sstat&stop_sequence=1"

LINE_MAPPING = {
	"Worcester": "CR-Worcester"
}

def open_stream(stop):
	stream_url = API_URL.format(route=LINE_MAPPING[stop])

	stream_response = subprocess.Popen([
                'curl',
                '-sfN',
                '-H',
                "accept: text/event-stream",
                '-H',
                "x-api-key: {}".format(API_KEY),
                stream_url],
                stdout=subprocess.PIPE,
                bufsize=1
	)

	event_type = None
	data_string = None
	predictions = {}
	for line in iter(stream_response.stdout.readline, b''):
		print_str = None
		message = line.split(':',1)
		if len(message) != 2:
			continue
		message_type = message[0].strip()

		if message_type == 'event':
			event_type = message[1].strip()
		elif message_type == 'data':
			data_string = message[1]
			json_data = json.loads(data_string)

			for row in json_data:
				p_id = row['id']
				if 'relationships' in row:
					relationships = row['relationships']
				if 'attributes' in row:
					attributes = row['attributes']

			if event_type == 'reset':
				route_id = relationships['route']['data']['id']
				stop_id = relationships['stop']['data']['id']
				status = attributes['status']
				departure_time = attributes['departure_time'] #needs strptime
				predictions[p_id] = [route_id,stop_id,status,departure_time]

				print_str = """
					Current Commuter Rail departures from South Station:
					Stop: {}, Line: {}, Departure Time: {}, Status: {}
				""".format(stop_id,route_id,departure_time,status)
			elif event_type == 'add':
				pass
			elif event_type == 'remove':
				del predictions[prediction_id]
			else:
				pass
			event_type = None
		else:
			event_type = None
			data_string = None

		if print_str:
			print(print_str.replace('\t',''))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-l","--line",help="Specify which line you would like to see departures for")
	args = parser.parse_args()

	line = args.line if args.line else "Worcester"
	open_stream(line)

if __name__ == '__main__': main()

