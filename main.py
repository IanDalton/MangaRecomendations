import requests,asyncio,json,csv, os,aiohttp
from dotenv import load_dotenv

load_dotenv()
MAL_CLIENT_ID = os.getenv("MAL_CLIENT_ID")
request_sleep_time_ms = 4000


async def get_user_data(users: set, list: str = "mangalist"):
    if list not in ["mangalist", "animelist"]:
        raise ValueError("list must be either 'mangalist' or 'animelist'")
    responses = {}
    async with aiohttp.ClientSession() as session:
        for user in users:
            await asyncio.sleep(request_sleep_time_ms / 1000)
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
async def get_content_data(content_id:str,content_type:str="manga"):
    if content_type not in ["manga","anime"]:
        raise ValueError("content_type must be either 'manga' or 'anime'")
    await asyncio.sleep(request_sleep_time_ms / 1000)
    response = requests.get(f"https://api.myanimelist.net/v2/{content_type}/{content_id}?fields=[genres,authors,background,start_date,status,popularity,rank,synopsis,mean,num_list_users,num_scoring_users,nsfw,num_chapters]", headers={"X-MAL-CLIENT-ID":MAL_CLIENT_ID})
    return json.loads(response.text)

async def get_ranking_data(content_type:str="manga", limit:int = 5000):
    max_limit = 500
    if content_type not in ["manga","anime"]:
        raise ValueError("content_type must be either 'manga' or 'anime'")
    responses = []
    async with aiohttp.ClientSession() as session:
        for i in range(limit//max_limit):
            await asyncio.sleep(request_sleep_time_ms / 1000)
            async with session.get(f"https://api.myanimelist.net/v2/{content_type}/ranking?limit={max_limit}&offset={max_limit*(i)}", headers={"X-MAL-CLIENT-ID":MAL_CLIENT_ID}) as response:
                data = await response.text()
                #print(data)
                responses.extend(json.loads(data)["data"])
                
    return {"data": responses}


async def get_active_users(content_type:str="manga",pages = 10,topic=49494) -> set:
    if content_type not in ["manga","anime"]:
        raise ValueError("content_type must be either 'manga' or 'anime'")
    #requests_per_second = 1
    usernames = set()
    async with aiohttp.ClientSession() as session:
        for i in range(pages):
            await asyncio.sleep(request_sleep_time_ms / 1000)
            async with session.get(f"https://api.myanimelist.net/v2/forum/topic/{topic}?limit=100&offset={100*i}",headers={"X-MAL-CLIENT-ID":MAL_CLIENT_ID}) as response:
                data = await response.text()
                #print(data)
                data = json.loads(data)["data"]["posts"]
                for item in data:
                    usernames.add(item["created_by"]["name"])
    return usernames

user_list = ["TheMissingTrex","Cyxxar","Jseph22"]

async def main():

    if not os.path.exists("users.txt"):
        active_users = await get_active_users(pages=10)
        print("Active users: ",active_users)
        with open("users.txt","w") as f:
            for user in active_users:
                f.write(user + "\n")
    else:
        with open("users.txt","r") as f:
            active_users = f.readlines()
            active_users = [user.strip() for user in active_users]


    
    user_list.extend(active_users)
    for file in os.listdir("user"):
        user_list.remove(file.replace(".json",""))




    results = await get_user_data(user_list)


    
    #save the results to json
    for i in range(len(user_list)):
        with open(f"user/{user_list[i]}.json","w") as f:
            json.dump(results[i],f,indent=4)
    


    
    
    #save the results to csv
    with open("output.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user","manga_id","status","is_rereading","score","chapters_read","updated_at"])
        for i in range(len(user_list)):
            try:
                for item in results[i]["data"]:
                    writer.writerow([user_list[i],item["node"]["id"],item["list_status"]["status"],item["list_status"]["is_rereading"],item["list_status"]["score"],item["list_status"]["num_chapters_read"],item["list_status"]["updated_at"]])
            except:
                print(f"Error with {user_list[i]}")
                continue

asyncio.run(main())


