import googleapiclient.discovery
from pprint import pprint
import sys
from googleapiclient.errors import HttpError
import pymongo
from pymongo import MongoClient
import mysql.connector
import pandas as pd
import json
from datetime import datetime
import streamlit as st
from streamlit_option_menu import option_menu

channel_id1="UCOtCKIoHcQvBl1GzRo7Z2SA" #Go4x4 
channel_id2="UCtGbExCzlwmsyWKpxLnyEww" #shubh
channel_id3="UCPRlk51FNmMnIgF0I3A7N_Q" #Lotus Cakes
channel_id4="UCQdE0I8SP4WKIg42oivvF9Q" #Kandra
channel_id5="UCY1kMZp36IQSyNx_9h4mpCg" #mark rober
channel_id6="UCj0aKGrBN6x2_PY0c6RrGNw" #Fanilo Andrianasolo
channel_id7="UCZjRcM1ukeciMZ7_fvzsezQ" #coding is fun
channel_id8="UCQeWT4fMOC8zgh3vtn83KVw" #junior tales
channel_id9="UCmSJaNF_2BFeah-Q1cM7c6A" #writeup stories
channel_id10="UCnSBH14-eDPf-B39ueNG0-g" #kiddiee tales
channel_id=channel_id10


api_key1="AIzaSyAe7chpUyFRqYu3Y6FnULzNl6pPkEs04iM"
api_key2="AIzaSyA0t7cl3lP8N_J3Edy_25AzlSNOs6Z7P4o"
api_key3="AIzaSyCIeDfCvAqON3vm6haold0pnFGeG_FjDpg"
api_key=api_key3

client=pymongo.MongoClient('mongodb+srv://jeriyl:atlas12345@youtubeproject.ockmy5w.mongodb.net/')
db=client["YouTube_Project"]
collection=db["YouTube_Channels"]

sys.stdout.reconfigure(encoding='utf-8')

def get_channel_details(channel_id):
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key)
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()
    for i in response["items"]:
        channeldata=dict(
            CHANNEL_NAME=i['snippet']['title'],
            CHANNEL_ID=i['id'],
            SUBSCRIPTION_COUNT=i['statistics']['subscriberCount'],
            CHANNEL_VIEWS=i['statistics']['viewCount'],
            CHANNEL_DESCRIPTION=i['snippet']['localized']['description'],
            PLAYLIST_ID=i['contentDetails']['relatedPlaylists']['uploads'],
            TOTAL_VIDEOS=i['statistics']['videoCount']
            )
    return channeldata
def get_video_id(channel_id):
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()

def get_video_ids(channel_id):
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key)
    next_page_token=None
    video_ids=[]
    response=youtube.channels().list(part="contentDetails",
                                        id=channel_id).execute()
    playlist_id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    #print(playlist_id)
    while True:
        request = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token)
        response1 = request.execute()

        for i in range(len(response1['items'])):
            videoid=response1['items'][i]['snippet']['resourceId']['videoId']
            video_ids.append(videoid)
        next_page_token=response1.get('nextPageToken')

        if next_page_token is None:
            break
    return(video_ids)

total_video_ids=get_video_ids(channel_id)
#pprint(total_video_ids)

# Set default encoding to 'utf-8'
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def video_details(listofids):
    video_datas=[]
    for x in total_video_ids:
        youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key)
        request=youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=x)
        response=request.execute()

        for item in response['items']:
            
            video_data=dict(
                CHANNEL_NAME=item['snippet']['channelTitle'],
                VIDEO_NAME=item['snippet']['localized']['title'],
                VIDEO_ID=item['id'],
                VIDEO_DESCRIPTION=item['snippet']['description'],
                VIDEO_TAGS= item['snippet'].get('tags'),
                PUBLISHED_DATE=item['snippet']['publishedAt'],
                VIEW_COUNT=item['statistics'].get('viewCount'),
                LIKE_COUNT=item['statistics'].get('likeCount'),
                FAVOURITE_COUNT=item['statistics']['favoriteCount'],
                COMMENTS_COUNT=item['statistics'].get('commentCount'),
                DURATION=item['contentDetails']['duration'],
                THUMBNAIL=item['snippet']['thumbnails']['default']['url'],
                CAPTION_STATUS=item['contentDetails']['caption']
            )
        video_datas.append(video_data)
    return video_datas
    
#channel_video_details=video_details(total_video_ids)
#print(len(channel_video_details))
#pprint(channel_video_details)

def comment_details(v_ids):
    comment_datas = []
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key)
    for comment_id in v_ids:
        try:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=comment_id,
                maxResults=50)
            response = request.execute()
            
            for item in response['items']:
                comment_data = {
                    'COMMENT_ID': item['id'],
                    'AUTHOR_NAME': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    'PUBLISHED_DATE': item['snippet']['topLevelComment']['snippet']['publishedAt'],
                    'COMMENT_TEXT': item['snippet']['topLevelComment']['snippet']['textDisplay']
                }
                comment_datas.append(comment_data)
                
        except HttpError as e:
            if e.resp.status == 403:
                #print(f"Comments are disabled for video with ID: {comment_id}. Skipping...")
                pass
            else:
                raise
        except ImportError as e:
            print("Error importing HttpError from googleapiclient.errors:", e)
            
    return(comment_datas)

#video_comment_details=comment_details(total_video_ids)
#pprint(video_comment_details)
#print("Comment Details are Obtained!")

def playlist_details(channel_id):
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_key)
    playlist_datas=[]
    request = youtube.playlists().list(
            part="snippet,contentDetails",
            channelId=channel_id,
            maxResults=50)
    response = request.execute()
    #pprint(response)

    for item in response['items']:
        playlist_data=dict(
            CHANNEL_NAME=item['snippet']['channelTitle'],
            PLAYLIST_ID=item['id'],
            TITLE=item['snippet']['title'],
            CHANNEL_ID=item['snippet']['channelId']
        )
        playlist_datas.append(playlist_data)

    return(playlist_datas)
#playlist_info=playlist_details(channel_id)
#pprint(playlist_info)

def channels(channel_id):
    Channel=get_channel_details(channel_id)
    list_video_id= get_video_ids(channel_id)
    Video= video_details(total_video_ids)
    Comments=comment_details(total_video_ids)
    Playlist=playlist_details(channel_id)

    collection.insert_one({"Channel-Details":Channel,
                    "Video-Details":Video,
                    "Comments-Details":Comments,
                    "Playlist-Details":Playlist})
    return("Uploaded Successfully")

mon_con=channels(channel_id)
    
def channel_table():
    database1 = mysql.connector.connect(
        user='root',
        password='mysql@123',
        database='YouTube_Project',
        host='localhost'
    )
    cursor=database1.cursor()
    
    drop_query= """drop table if exists channel_details_table"""
    cursor.execute(drop_query)
    database1.commit()

    try:
        create_channel_table='''create table if not exists channel_table(CHANNEL_NAME varchar(50),
                                                                                CHANNEL_ID varchar(100) primary key,
                                                                                CHANNEL_DESCRIPTION text,
                                                                                CHANNEL_VIEWS bigint,
                                                                                SUBSCRIPTION_COUNT bigint,
                                                                                PLAYLIST_ID varchar(100),
                                                                                TOTAL_VIDEOS bigint)'''
        cursor.execute(create_channel_table)
        database1.commit()

    except:
        print("Table already created!")

    channel_list=[]
    client=pymongo.MongoClient('mongodb+srv://jeriyl:atlas12345@youtubeproject.ockmy5w.mongodb.net/')
    db=client["YouTube_Project"]
    coll1=db["YouTube_Channels"]
    for ch_data in coll1.find({},{"_id":0,"Channel-Details":1}):
        channel_list.append(ch_data['Channel-Details'])

    df=pd.DataFrame(channel_list)
    #print(df)

    for index, row in df.iterrows():
        insert_values = """INSERT INTO channel_table (CHANNEL_NAME,
                                                            CHANNEL_ID,
                                                            CHANNEL_DESCRIPTION,
                                                            CHANNEL_VIEWS,
                                                            SUBSCRIPTION_COUNT,
                                                            PLAYLIST_ID,
                                                            TOTAL_VIDEOS)
                        VALUES (%s, %s, %s, %s, %s, %s)"""
        values = (row['CHANNEL_NAME'],
                row['CHANNEL_ID'],
                row['CHANNEL_DESCRIPTION'],
                row['CHANNEL_VIEWS'],
                row['SUBSCRIPTION_COUNT'], 
                row['PLAYLIST_ID'],
                row['TOTAL_VIDEOS'])
        try:
            cursor.execute(insert_values, values)
            database1.commit()
        except:
            pass

def video_table():
    database1 = mysql.connector.connect(
        user='root',
        password='mysql@123',
        database='YouTube_Project',
        host='localhost'
    )
    cursor = database1.cursor()

    video_list = []
    client=pymongo.MongoClient('mongodb+srv://jeriyl:atlas12345@youtubeproject.ockmy5w.mongodb.net/')
    db=client["YouTube_Project"]
    coll1=db["YouTube_Channels"]
    try:
        create_video_table = '''create table if not exists video_table(
                                                                CHANNEL_NAME varchar(150),
                                                                VIDEO_NAME varchar(150),
                                                                VIDEO_ID varchar(150) primary key,
                                                                VIDEO_DESCRIPTION text,
                                                                VIDEO_TAGS text,
                                                                PUBLISHED_DATE timestamp,
                                                                VIEW_COUNT bigint,
                                                                LIKE_COUNT bigint,
                                                                FAVOURITE_COUNT bigint,
                                                                COMMENTS_COUNT bigint,
                                                                DURATION varchar(50),
                                                                THUMBNAIL varchar(200),
                                                                CAPTION_STATUS varchar(10)
                                                                )'''
        cursor.execute(create_video_table)
        database1.commit()
    except mysql.connector.Error as e:
        print("Error creating video_table:", e)

    for video_data in coll1.find({}, {"_id": 0, "Video-Details": 1}):
        for i in range(len(video_data['Video-Details'])):
            video_list.append(video_data['Video-Details'][i])

    df2 = pd.DataFrame(video_list)
    df2.replace({pd.NA: None}, inplace=True)

    for index, row in df2.iterrows():
        try:
            channel_name = row['CHANNEL_NAME']
            video_name = row['VIDEO_NAME']
            video_id = row['VIDEO_ID']
            video_description = row['VIDEO_DESCRIPTION']
            video_tags = json.dumps(row['VIDEO_TAGS'])
            published_date = datetime.strptime(row['PUBLISHED_DATE'], '%Y-%m-%dT%H:%M:%SZ')
            view_count = row['VIEW_COUNT']
            like_count = row['LIKE_COUNT']
            favourite_count = row['FAVOURITE_COUNT']
            comments_count = row['COMMENTS_COUNT']
            duration = row['DURATION']
            thumbnail = row['THUMBNAIL']
            caption_status = row['CAPTION_STATUS']

            insert_values = """INSERT INTO video_table(CHANNEL_NAME,
                                                            VIDEO_NAME,
                                                            VIDEO_ID,
                                                            VIDEO_DESCRIPTION,
                                                            VIDEO_TAGS,
                                                            PUBLISHED_DATE,
                                                            VIEW_COUNT,
                                                            LIKE_COUNT,
                                                            FAVOURITE_COUNT,
                                                            COMMENTS_COUNT,
                                                            DURATION,
                                                            THUMBNAIL,
                                                            CAPTION_STATUS)
                                                                
                            values (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s, %s)"""

            values = tuple([channel_name, video_name, video_id, video_description,
                            video_tags, published_date, view_count, like_count,
                            favourite_count, comments_count, duration, thumbnail,
                            caption_status])

            cursor.execute(insert_values, values)
            database1.commit()
            
        except mysql.connector.IntegrityError as e:
            #print("Duplicate entry error:", e)
            # Optionally, you can log this error or handle it as per your application's requirements.
            # For example, you can choose to skip the duplicate entry and continue with the next iteration.
            continue
        except Exception as e:
            print("Error inserting record:", e)
            # Handle other exceptions here as needed.

    cursor.close()
    database1.close()

#video_table()

def comments_table():
    database1 = mysql.connector.connect(
            user='root',
            password='mysql@123',
            database='YouTube_Project',
            host='localhost'
        )
    cursor=database1.cursor()
    drop_query= """drop table if exists comments_table"""
    cursor.execute(drop_query)
    database1.commit()

    try:
        create_comments_table='''create table if not exists comments_table(
                                                                    AUTHOR_NAME varchar(50),
                                                                    COMMENT_ID varchar(150) primary key,
                                                                    COMMENT_TEXT text,
                                                                    PUBLISHED_DATE timestamp
                                                                    )'''
        cursor.execute(create_comments_table)
        database1.commit()
    except:
         print("COMMENTS TABLE IS ALREADY CREATED")

    comments_list=[]
    client=pymongo.MongoClient('mongodb+srv://jeriyl:atlas12345@youtubeproject.ockmy5w.mongodb.net/')
    db=client["YouTube_Project"]
    coll1=db["YouTube_Channels"]
    for comments_data in coll1.find({},{"_id":0,"Comments-Details":1}):
        for i in range(len(comments_data['Comments-Details'])):
            comments_list.append(comments_data['Comments-Details'][i])

            
    df3=pd.DataFrame(comments_list)
    #print(df3)

    df3.replace({pd.NA: None}, inplace=True)
    for index, row in df3.iterrows():
                    insert_values = """INSERT IGNORE INTO comments_table(COMMENT_ID,
                                                                    AUTHOR_NAME,
                                                                    PUBLISHED_DATE,
                                                                    COMMENT_TEXT
                                                                    )
                                VALUES (%s, %s, %s, %s)"""
                    values = (row['COMMENT_ID'],
                        row['AUTHOR_NAME'],
                        row['PUBLISHED_DATE'],
                        row['COMMENT_TEXT'])
                
                    try:
                        cursor.execute(insert_values, values)
                        database1.commit()
                    except:
                        print("COMMENT TABLE VALUES ARE ALREADY INSERTED")

#comments_table()

def playlist_table():
    database1 = mysql.connector.connect(
        user='root',
        password='mysql@123',
        database='YouTube_Project',
        host='localhost'
    )
    cursor=database1.cursor()

    drop_query= """drop table if exists playlist_details_table"""
    cursor.execute(drop_query)
    database1.commit()

    try:
        create_playlist_table='''create table if not exists playlist_table(PLAYLIST_ID varchar(50) primary key,
                                                                                    TITLE varchar(100),
                                                                                    CHANNEL_ID varchar(100),
                                                                                    CHANNEL_NAME varchar(50)
                                                                                    )'''
        cursor.execute(create_playlist_table)
        database1.commit()
    except:
         print("PLAYLIST TABLE IS ALREADY CREATED")

    playlist_list=[]
    client=pymongo.MongoClient('mongodb+srv://jeriyl:atlas12345@youtubeproject.ockmy5w.mongodb.net/')
    db=client["YouTube_Project"]
    coll1=db["YouTube_Channels"]
    for pl_data in coll1.find({},{"_id":0,"Playlist-Details":1}):
        for i in range(len(pl_data['Playlist-Details'])):
            playlist_list.append(pl_data['Playlist-Details'][i])

            
    df4=pd.DataFrame(playlist_list)
    #print(df4)

    df4.replace({pd.NA: None}, inplace=True)


    for index, row in df4.iterrows():
            insert_values = """INSERT IGNORE INTO playlist_table(PLAYLIST_ID,
                                                                TITLE,
                                                                CHANNEL_ID,
                                                                CHANNEL_NAME
                                                                )
                            VALUES (%s, %s, %s, %s)"""
            values = (row['PLAYLIST_ID'],
                    row['TITLE'],
                    row['CHANNEL_ID'],
                    row['CHANNEL_NAME'])
            
            try:
                    cursor.execute(insert_values, values)
                    database1.commit()
            except:
                    print("PLAYLIST VALUES ARE ALREADY INSERTED")

#playlist_table()

def tables():
     channel_table()
     video_table()
     comments_table()
     playlist_table()

     return "ALL TABLES ARE CREATED SUCCESSFULLY"

#Tables=tables()

def show_channel_table():
    channel_list=[]
    database=client["YouTube_Project"]
    coll1=database["YouTube_Channels"]
    for ch_data in coll1.find({},{"_id":0,"Channel-Details":1}):
        channel_list.append(ch_data['Channel-Details'])

    df1=st.dataframe(channel_list)
    return df1

def show_video_table():
    video_list = []
    database=client["YouTube_Project"]
    coll1=database["YouTube_Channels"]
    for video_data in coll1.find({}, {"_id": 0, "Video-Details": 1}):
        for i in range(len(video_data['Video-Details'])):
            video_list.append(video_data['Video-Details'][i])

    df2 = st.dataframe(video_list)
    return df2

def show_comments_table():
    comments_list=[]
    database=client["YouTube_Project"]
    coll1=database["YouTube_Channels"]
    for comments_data in coll1.find({},{"_id":0,"Comments-Details":1}):
        for i in range(len(comments_data['Comments-Details'])):
            comments_list.append(comments_data['Comments-Details'][i])
         
    df3=st.dataframe(comments_list)
    return df3

def show_playlist_table():
    playlist_list=[]
    database=client["YouTube_Project"]
    coll1=database["YouTube_Channels"]
    for pl_data in coll1.find({},{"_id":0,"Playlist-Details":1}):
        for i in range(len(pl_data['Playlist-Details'])):
            playlist_list.append(pl_data['Playlist-Details'][i])
    
            
    df4=st.dataframe(playlist_list)
    return df4

st.title("YOUTUBE DATA HARVESTING AND WAREHOUSING")
st.markdown("___________")

selected=option_menu(menu_title="YOUTUBE DATA HARVESTING AND WAREHOUSING",
                        options=["Data Collection","Store in MongoDB","Migration of Data","Data Analysis"],
                    icons=["archive","cloud-upload","database-add","search"],
                    default_index=0,
                    orientation="horizontal"
                    )

data = {
        'Channel Name': ['Go4x4', 'Shubh', 'Lotus Cakes', 'Kandra', 'Mark Rober',
                         'Fanilo Andrianasolo','Junior Tales','Coding is Fun'],
        'Channel ID': ["UCOtCKIoHcQvBl1GzRo7Z2SA", "UCtGbExCzlwmsyWKpxLnyEww", "UCPRlk51FNmMnIgF0I3A7N_Q", 
                       "UCQdE0I8SP4WKIg42oivvF9Q", "UCY1kMZp36IQSyNx_9h4mpCg","UCj0aKGrBN6x2_PY0c6RrGNw",
                       "UCQeWT4fMOC8zgh3vtn83KVw","UCZjRcM1ukeciMZ7_fvzsezQ"]
    }
if selected == "Data Collection":
    st.write("Copy the Desired channel id from the Table")
    st.dataframe(data,hide_index=None)
elif selected =="Store in MongoDB":
    user_channel_id=st.text_input("Please provide the channel ID.")
    if st.button("Collect and store Data"):
        ch_ids=[]
        client=pymongo.MongoClient('mongodb+srv://jeriyl:atlas12345@youtubeproject.ockmy5w.mongodb.net/')
        db=client["YouTube_Project"]
        coll1=db["YouTube_Channels"]
        for ch_data in coll1.find({},{"_id":0,"Channel-Details":1}):
            ch_ids.append(ch_data["Channel-Details"]["CHANNEL_ID"])
        if user_channel_id in ch_ids:
            st.success("This channel details have already been recorded.")
        else:
            Channel=get_channel_details(user_channel_id)
            collection.insert_one({"Channel-Details":Channel})
            st.success(Channel)
elif selected =="Migration of Data":
    if st.button("Migrate to SQL"):
        tablesvar=tables()
        st.success(tablesvar)
        show_table=st.radio("Select the button for view",("Channel","Video","Comments","Playlist"))
        if show_table=="Channel":
            show_channel_table()
        elif show_table=="Video":
            show_video_table()
        elif show_table=="Comments":
            show_comments_table()
        elif show_table=="Playlist":
            show_playlist_table()
        else:
            print("Choose the appropriate option")






if selected == "Data Analysis":
    st.title("Data Analysis")
    question = st.selectbox("Choose the question to get the result.", (
        "1. What are the names of all the videos and their corresponding channels?",
        "2. Which channels have the most number of videos, and how many videos do they have?",
        "3. What are the top 10 most viewed videos and their respective channels?",
        "4. How many comments were made on each video, and what are their corresponding video names?",
        "5. Which videos have the highest number of likes, and what are their corresponding channel names?",
        "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
        "7. What is the total number of views for each channel, and what are their corresponding channel names?",
        "8. What are the names of all the channels that have published videos in the year 2022?",
        "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?",
        "10. Which videos have the highest number of comments, and what are their corresponding channel names?"
    ))

    database1 = mysql.connector.connect(
        user='root',
        password='mysql@123',
        database='YouTube_Project',
        host='localhost'
    )
    cursor = database1.cursor()

    if question == "1. What are the names of all the videos and their corresponding channels?":
        query1 = """select video_name as Video_Title , channel_name as Channel_Name from video_table"""
        cursor.execute(query1)
        t1 = cursor.fetchall()
        df1 = pd.DataFrame(t1,columns=["VIDEO NAME","CHANNEL_NAME"])
        st.write(df1)

    elif question == "2. Which channels have the most number of videos, and how many videos do they have?":
        query2 = """select channel_name as Channel_name , total_videos as Videos_count from channel_table
                    order by total_videos desc"""
        cursor.execute(query2)
        t2 = cursor.fetchall()
        df2 = pd.DataFrame(t2,columns=["CHANNEL NAME","VIDEO COUNT"])
        st.write(df2)

    else:
        print("error")


