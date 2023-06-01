#! python3
#  PyTOBS.py -- Automatically downloads images from Reddit and sets them to the user's backround.

import os, sys
import requests
import random
import logging
import argparse
from io import BytesIO
from itertools import islice

from PIL import Image
import praw
from prawcore import exceptions

import back_switch



# Global Variables, settings, etc
# fmt: off
min_res_x  = 600                    # Minimum width of images to use as backgrounds
min_res_y  = 800                    # Minimum height of images to use as backgrounds
directory  = "PyTOBSBackgrounds"    # Where background images will be stored
resolution = (1920,1080)            # User's desktop resolution stored in a tuple (width,height)
# fmt: on

cli_id = "SiNEa2xmai5BJNYiK3zs5Q"
cli_secret = "QmQn510s48D3troFhqCi5ml_lDSnoA"
use_agent = "python:PyTOBS:v0.1(by u/tobsdev)"
LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(message)s'
LOG_LEVEL = logging.INFO


def main(subs):
    if len(subs) < 1:
        logging.warning(f"No subreddits provided via -s command line argument. Using 'corgi'")
        subreddits = ["corgi"]
    else:
        subreddits = subs
        
    # Create Reddit Instance
    reddit = praw.Reddit(
        client_id=cli_id,
        client_secret=cli_secret,
        user_agent=use_agent,
    )

    # Build Subreddit Search String
    random.shuffle(subreddits)
    subredditString = "+".join(subreddits)

    # Create directory to save images into
    os.makedirs(directory, exist_ok=True)

    subLimit = 10
    skipFirst = 0
    imageFound = False
    checkedUrls = []

    while not imageFound:
        try:
            for submission in islice(reddit.subreddit(subredditString).hot(limit=subLimit),skipFirst,None):
                if submission.url in checkedUrls:
                    continue
                checkedUrls.append(submission.url)
                if any(submission.url.endswith(extension) for extension in [".png", ".jpg"]):
                    # See if we've already downloaded this image; skip if so.
                    subDirectory = submission.subreddit_name_prefixed[2:]
                    filename = os.path.join(directory, subDirectory, os.path.basename(submission.url))
                    if os.path.exists(filename):
                        continue

                    # Get the image
                    res = requests.get(submission.url)
                    res.raise_for_status()

                    # Check to see if the image is big enough
                    image = Image.open(BytesIO(res.content))
                    width, height = image.size
                    image.close()
                    if (width > min_res_x) and (height > min_res_y):
                        # Download the image
                        imageFound = True
                        
                        # Create image subdirectory if needed.
                        os.makedirs(os.path.join(directory, subDirectory), exist_ok=True)
                        with open(
                            os.path.join(directory, subDirectory, os.path.basename(submission.url)), "wb"
                        ) as imageFile:
                            for chunk in res.iter_content(100000):
                                imageFile.write(chunk)
                            backgroundImageLoc = os.path.abspath(
                                os.path.join(directory, subDirectory, os.path.basename(submission.url))
                            )
                        logging.info(f"Successfully downloaded {submission.url} from {subDirectory}") 
                        break
            subLimit += 10
            skipFirst += 10
        except exceptions.Redirect as exception:
            logging.exception("Subreddit " + str(subreddits) + " not found, redirected to Search.")
            sys.exit()
        except praw.exceptions.RedditAPIException as exception:
            for subexception in exception.items:
                logging.exception(subexception.error_type)
            sys.exit()
    # This should never happen, but just in case the above code found no images at all
    if not imageFound:
        print("Couldn't find an image in subreddits " + subreddits)
        sys.exit()

    # Determine optimal fit based off image dimensions.
    fit = back_switch.get_fit_style(backgroundImageLoc, resolution)

    # Set user's background to the new image with the optimal fit.
    back_switch.change_wallpaper(backgroundImageLoc, fit)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type = str, help = "Subreddits to check, separated by comma", default = "Corgi,Wallpaper")

    logging.basicConfig(filename='pytobs_results.log',level=LOG_LEVEL, format=LOG_FORMAT)
    
    args = parser.parse_args()
    subs = args.s.split(",")
    
    try:
        main(subs)
    except Exception as err:
        logging.exception("Error -- " + str(err))
        sys.exit()
