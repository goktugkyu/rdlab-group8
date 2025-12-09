
import os

import ssl

from irods.session import iRODSSession

from tqdm import tqdm



# Load iRODS environment file

try:

    env_file = os.environ['IRODS_ENVIRONMENT_FILE']

except KeyError:

    env_file = os.path.expanduser('~/.irods/irods_environment.json')



# SSL settings

ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)

ssl_settings = {'ssl_context': ssl_context}



# iRODS → local base paths

irods_base_path = "/set/home/ciis-lab/datasets/epic-kitchens/videos_640x360"

local_base_path = "/data/leuven/380/vsc38053/RD_Project/epic-kitchens-data/videos_640x360"



with iRODSSession(irods_env_file=env_file, **ssl_settings) as session:



    irods_collection = session.collections.get(irods_base_path)

    participants = [obj.name for obj in irods_collection.subcollections]



    for participant in tqdm(participants, desc="Downloading participants", unit="participant"):



        participant_local_path = os.path.join(local_base_path, participant)

        os.makedirs(participant_local_path, exist_ok=True)



        participant_collection = session.collections.get(

            f"{irods_base_path}/{participant}"

        )



        for data_obj in tqdm(participant_collection.data_objects,

                             desc=f"{participant}", leave=False, unit="video"):



            if not (data_obj.name.endswith('.mp4') or data_obj.name.endswith('.MP4')):

                continue



            irods_video_path = f"{irods_base_path}/{participant}/{data_obj.name}"

            local_video_path = os.path.join(participant_local_path, data_obj.name)



            if not os.path.exists(local_video_path):

                session.data_objects.get(irods_video_path, local_video_path)


