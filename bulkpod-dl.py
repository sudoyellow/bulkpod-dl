import feedparser
import requests
import os
import re
import time
import platform
from tqdm import tqdm  # Import tqdm for the progress bar

# Function to clear the screen based on OS
def clear_screen():
    os_system = platform.system()
    if os_system == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# Function to test the entered RSS feed and display show information
def test_rss_feed(rss_url):
    feed = feedparser.parse(rss_url)
    
    # Check if the feed has a title and description
    if feed.bozo:
        print("\n(!) Invalid RSS feed URL. Please check the URL and try again.")
        input("\nPress Enter to return to the main menu...")
        return None, "", 0  # Return None for feed and empty strings for title and count
    
    # Extract show information
    show_title = feed.feed.get('title', 'Unknown Title')
    show_description = feed.feed.get('description', 'No description available.')
    show_copyright = feed.feed.get('copyright', 'Unknown Copyright')
    episode_count = len(feed.entries)
    
    clear_screen()
    print("---------------( bulkpod-dl )---------------")
    print("\nShow Information:")
    print("-----------------")
    print(f"           Title: {show_title}")
    print(f"   # of Episodes: {episode_count}")
    print(f"       Copyright: {show_copyright}")
    print("\nShow Description:")
    print("-----------------")
    print(f'"{show_description}"')
    
    # Wait for user to press Enter to return to the main menu
    input("\nPress Enter to return to the main menu...")

    return feed, show_title, episode_count

# Function to download the episodes
def download_episodes(feed):
    # Create a directory to store the episodes
    os.makedirs("bulkpod-downloads", exist_ok=True)

    # Calculate the total number of episodes
    total_episodes = len(feed.entries)

    # Regular expression pattern to remove invalid characters from filenames
    invalid_characters = r'[<>:"/\\|?*]'

    # Retry configuration
    MAX_RETRIES = 5  # Number of retries
    RETRY_DELAY = 5  # Seconds between retries

    # List to store episodes that failed to download
    failed_episodes = []

    # Loop through the episodes and download them
    for idx, entry in enumerate(feed.entries, start=1):
        episode_url = entry.enclosures[0].href  # Get the episode URL
        episode_title = entry.title  # Get the episode title

        # Sanitize the episode title by removing invalid characters
        sanitized_title = re.sub(invalid_characters, '_', episode_title)

        # Ensure the filename is safe and avoid overwriting files with the same name
        episode_filename = os.path.join("bulkpod-downloads", f"{sanitized_title}.mp3")

        # Check if the episode file already exists
        if os.path.exists(episode_filename):
            print(f"Skipping {episode_title} as it's already downloaded.")
            continue  # Skip downloading this episode if it's already downloaded

        # Display a progress bar for each episode download
        print(f"\nDownloading episode {idx}/{total_episodes}: {episode_title}")

        # Retry mechanism for downloading the episode
        retries = 0
        while retries < MAX_RETRIES:
            try:
                # Make the request to download the episode
                response = requests.get(episode_url, stream=True, timeout=30)  # Add timeout for requests

                # Get the total file size (in bytes) from the response headers
                total_size = int(response.headers.get('content-length', 0))

                # Write the episode to file with a progress bar
                with open(episode_filename, 'wb') as f, tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=episode_title
                ) as bar:
                    # Download in chunks
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            bar.update(len(chunk))  # Update the progress bar

                print(f"Downloaded: {episode_title}")
                break  # Exit the retry loop if successful

            except requests.exceptions.RequestException as e:
                retries += 1
                print(f"Error downloading episode {episode_title}: {e}")
                print(f"Retrying {retries}/{MAX_RETRIES}...")
                time.sleep(RETRY_DELAY)  # Wait before retrying

        # If it fails after MAX_RETRIES, skip the episode and add it to the failed episodes list
        if retries == MAX_RETRIES:
            print(f"Failed to download {episode_title} after {MAX_RETRIES} retries.")
            failed_episodes.append(episode_title)  # Add failed episode to the list

    # After processing all episodes, display the failed episodes
    print("\nAll episodes processed!")

    if failed_episodes:
        print("\nThe following episodes failed to download:")
        for failed_episode in failed_episodes:
            print(f"- {failed_episode}")
    else:
        print("All episodes were downloaded successfully.")

# Main function to display the menu and interact with the user
def main():
    feed = None  # Initialize feed variable to None
    show_title = ""  # Initialize show title
    episode_count = 0  # Initialize episode count
    
    while True:
        clear_screen()
        print("---------------( bulkpod-dl )---------------")
        print("1. Enter RSS feed and test feed information")
        print("2. Download episodes")
        print("3. Exit")

        # Show the current loaded RSS feed, if any
        if feed:
            print(f"\nRSS feed: {show_title} ({episode_count} episodes)")
        else:
            print("\nRSS feed: No RSS feed loaded.")
        
        choice = input("\nPlease select an option (1/2/3): ").strip()
        
        if choice == '1':
            rss_url = input("\nEnter the RSS feed URL: ").strip()
            feed, show_title, episode_count = test_rss_feed(rss_url)
            # Feed will be None if the URL is invalid, and we return to the menu
            if feed:
                print("\nRSS feed test completed successfully!")
                time.sleep(2)
        
        elif choice == '2':
            clear_screen()
            print("---------------( bulkpod-dl )---------------\n")
            if feed:
                download_episodes(feed)
            else:
                print("\n(!) Please test an RSS feed first (Option 1)!")
                time.sleep(1)
        
        elif choice == '3':
            print("\nExiting bulkpod-dl by Yellowjacket (c) 2025")
            print("X = @sudoyellow | GitHub: sudoyellow\n")
            time.sleep(1)
            break
        
        else:
            print("\n(!) Invalid option! Try again.")
            time.sleep(1)

# Run the main function to start the script
if __name__ == "__main__":
    main()
