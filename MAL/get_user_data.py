import requests,asyncio,json,csv, os,aiohttp
from dotenv import load_dotenv

async def get_user_data(users: set,MAL_CLIENT_ID:str, list: str = "mangalist"):
    if list not in ["mangalist", "animelist"]:
        raise ValueError("list must be either 'mangalist' or 'animelist'")
    responses = {}
    async with aiohttp.ClientSession() as session:
        for user in users:
            #await asyncio.sleep(4)
            print(f"Getting data for {user}")
            retries = 3  # Number of retries
            for attempt in range(retries):
                try:
                    async with session.get(f"https://api.myanimelist.net/v2/users/{user}/{list}?limit=1000&fields=list_status", headers={"X-MAL-CLIENT-ID": MAL_CLIENT_ID}) as response:
                        if response.status == 200 or  response.status == 403 or response.status == 404:
                            data = await response.text()
                            data_dict = json.loads(data)
                            with open(f"user/{user}.json", "w") as f:
                                json.dump(data_dict, f, indent=4)
                            if "error" in data_dict.keys():
                                print(f"Error with {user}: {data_dict['message']}")
                                break  # Exit the retry loop on server-reported error
                            responses[user] = data_dict.get("data", {})
                            break  # Successful request, exit the retry loop
                      

                        else:
                            print(f"Request failed with status {response.status}, attempt {attempt + 1} of {retries}")
                except Exception as e:
                    print(f"Request exception: {e}, attempt {attempt + 1} of {retries}")
                
                if attempt < retries - 1:  # Wait before retrying unless it's the last attempt
                    print(f"Waiting 2 minutes before retrying...")
                    await asyncio.sleep(120)  # Wait for 2 minutes before retrying
                else:
                    print(f"All attempts failed for {user}.")
    return responses