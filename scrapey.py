import requests
import json
import time


class RateLimiter:
    def __init__(self):
        self.requests = []
        self.per_second_limit = 20
        self.per_two_minute_limit = 100

    def pause_champ(self):
        current_time = time.time()

        # Remove timestamps older than 2 minutes
        self.requests = [req_time for req_time in self.requests if current_time - req_time < 120]

        # Ensure the list is sorted in ascending order of timestamps
        self.requests.sort()

        while self.requests and len(self.requests) >= self.per_two_minute_limit:
            # Calculate sleep time to wait until just after the oldest request in the 2-minute window expires
            oldest_request = self.requests[0]
            sleep_time = max(120 - (current_time - oldest_request), 0) + 0.1  # Ensure sleep_time is non-negative
            print(f"Rate limit reached. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)
            current_time = time.time()
            self.requests = [req_time for req_time in self.requests if current_time - req_time < 120]

        if self.requests and len(self.requests) >= self.per_second_limit:
            # Calculate sleep time to wait until just after the 20th last request is older than 1 second
            twentieth_last_request = self.requests[-self.per_second_limit]
            sleep_time = max(1 - (current_time - twentieth_last_request), 0) + 0.1  # Ensure sleep_time is non-negative
            print(f"Approaching per-second limit. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)

        # Record the new request time after any necessary sleep
        self.requests.append(time.time())

def save_state_to_file(data, filename):
    """Saves data to a file."""
    with open(filename, 'w') as f:
        json.dump(list(data), f)  # Convert set to list for JSON serialization

def load_state_from_file(filename):
    """Loads data from a file, returning a list of dictionaries. If the file doesn't exist or is corrupt, returns an empty list."""
    try:
        with open(filename, 'r+') as f:
            try:
                data = json.load(f)  # Attempt to load existing data
                if not isinstance(data, list):  # Additional check to ensure data is a list
                    print("Warning: Data is not a list, resetting file with an empty list.")
                    raise json.JSONDecodeError("Data is not a list", doc="", pos=0)
                return data
            except json.JSONDecodeError:
                # Handle incomplete or corrupt JSON by resetting the file
                f.seek(0)  # Go to the beginning of the file
                f.truncate()  # Clear the file
                json.dump([], f)  # Initialize file with an empty list
                print("Warning: Corrupt JSON data in file, file has been reset to an empty list.")
                return []
    except FileNotFoundError:
        # If file doesn't exist, create it and initialize with an empty list
        with open(filename, 'w+') as f:
            print("No file found, creating new file with an empty list.")
            json.dump([], f)  # Initialize file with an empty list
        return []

def get_challenger(api_key, rate_limiter):
    api_url = "https://na1.api.riotgames.com/tft/league/v1/challenger"
    headers = {"X-Riot-Token": api_key}  # Standard header name
    
    try:
        response = requests.get(api_url, headers=headers)
        rate_limiter.pause_champ()

        if response.status_code == 200:            
            print("get_challenger: 200")
            data = response.json()
            return [entry["summonerId"] for entry in data.get("entries", [])] 
        else: 
            print("get challenger failed, using plebs")
            return ["SVl3E89xTvMRHILCrxrA48GygMdGih4qEyf-xaJFFb8c9tw", 
                    "5FBnLDL43thPLWmfBB6fOZ-cvPD_JnDP7lVE-jFPNpt8LdU",]
    except Exception as e:
        print(f"Exception occurred while getting challenger data: {e}")
        return []


def get_puuid(summonerId, api_key, rate_limiter):
    try:
        rate_limiter.pause_champ()
        api_url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}?api_key={api_key}"
        response = requests.get(api_url)
        if response.status_code == 200:
            print("get_puuid: 200")
            data = response.json()
            return data.get("puuid", "")
        else:
            print(f"Failed to get PUUID for {summonerId}: HTTP {response.status_code}")
            return ""
    except Exception as e:
        print(f"Exception occurred while getting PUUID for {summonerId}: {e}")
        return ""

def get_match_ids(puuid, api_key, rate_limiter):
    try:
        rate_limiter.pause_champ()
        api_url = f"https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?api_key={api_key}"
        response = requests.get(api_url)
        if response.status_code == 200:
            print("get_match_ids: 200")
            return response.json()
        else:
            print(f"Failed to get match IDs for {puuid}: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"Exception occurred while getting match IDs for {puuid}: {e}")
        return []
    
def get_match_data(match_id, api_key, rate_limiter):
    try:
        rate_limiter.pause_champ()
        api_url = f"https://americas.api.riotgames.com/tft/match/v1/matches/{match_id}?api_key={api_key}"
        response = requests.get(api_url)
        if response.status_code == 200:
            print("get_match_data: 200")
            return response.json()
        else:
            print(f"Failed to get match data for {match_id}: HTTP {response.status_code}")
            return {}
    except Exception as e:
        print(f"Exception occurred while getting match data for {match_id}: {e}")
        return {}
    
def get_summoner_name(summoner_id, api_key, rate_limiter):
    try:
        rate_limiter.pause_champ()
        api_url = f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key={api_key}"
        response = requests.get(api_url)
        if response.status_code == 200:
            print("get_summoner_name: 200")
            data = response.json()
            return data.get("name", "")
        else:
            print(f"Failed to get summoner name for {summoner_id}: HTTP {response.status_code}")
            return ""
    except Exception as e:
        print(f"Exception occurred while getting summoner name for {summoner_id}: {e}")
        return ""

def get_partticpants(puuids):
    match_data = load_state_from_file("match_data.json")

    for match in match_data:
        for participant_puuid in match["metadata"]["participants"]:
            if not any(participant['puuid'] == participant_puuid for participant in puuids):                
                puuids.append({"puuid": participant_puuid, "has_been_seen": False, "match_ids": []})
        save_state_to_file(puuids, "puuids.json")

def load_api_key():
    with open("api_key.txt", 'r') as f:
        return f.read().strip()
    
def process_challenger_summoners(api_key, rate_limiter):
    challenger_summoner_ids = get_challenger(api_key, rate_limiter)
    puuids = load_state_from_file("puuids.json")
    for summoner_id in challenger_summoner_ids:
            puuid = get_puuid(summoner_id, api_key, rate_limiter)
            if puuid and not any(d['puuid'] == puuid for d in puuids):
                summoner_name = get_summoner_name(summoner_id, api_key, rate_limiter)
                puuids.append({"puuid": puuid, "name": summoner_name, "has_been_seen": False, "match_ids": []})
                save_state_to_file(puuids, "puuids.json")

def process_match_data(api_key, rate_limiter, puuids):
    match_data = load_state_from_file("match_data.json")
    
    for puuid_entry in puuids:
        if not puuid_entry.get("has_been_seen", False):
            match_ids = get_match_ids(puuid_entry["puuid"], api_key, rate_limiter)
            puuid_entry["has_been_seen"] = True  # Mark the PUUID as seen
            for match_id in match_ids:
                if match_id not in puuid_entry["match_ids"]:
                    match_detail = get_match_data(match_id, api_key, rate_limiter)
                    match_data.append(match_detail)  # Append each match's data to the list
                    puuid_entry["match_ids"].append(match_id)  # Track which match IDs have been processed
                    # Update participant data if needed
                    save_state_to_file(match_data, "match_data.json")
            save_state_to_file(puuids, "puuids.json")
    #save everything to file after the for loop is done bc i hate myself
    save_state_to_file(puuids, "puuids.json")
    save_state_to_file(match_data, "match_data.json")


def main():
    api_key = load_api_key()
    rate_limiter = RateLimiter()

    puuids = load_state_from_file("puuids.json")

    process_challenger_summoners(api_key, rate_limiter) # Start with challenger people

    process_match_data(api_key, rate_limiter, puuids)   # Get match data for all the challenger people
    get_partticpants(puuids)                            # Get all the participants from the match data

if __name__ == "__main__":

    main()
