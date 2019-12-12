import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


"""
format of tree is
dict {
    tree_id: tree_id_text
    context: context text?
    first_story_block
    action_results: [act_res1, act_res2, act_res3...]
}

where each action_result's format is:
dict{
    action: action_text
    result: result_text
    action_results: [act_res1, act_res2, act_res3...]
}
"""


class Scraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--binary=/path/to/other/chrome/binary")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--window-size=1920x1080")
        exec_path = "/usr/local/bin/chromedriver"
        self.driver = webdriver.Chrome(
            chrome_options=chrome_options, executable_path=exec_path
        )
        self.max_depth = 10
        self.end_actions = {
            "End Game and Leave Comments",
            "Click here to End the Game and Leave Comments",
            "See How Well You Did (you can still back-page afterwards if you like)",
            "You have died.",
            "You have died",
            "Epilogue",
            "Save Game",
            "Your quest might have been more successful...",
            "5 - not the best, certainly not the worst",
            "The End! (leave comments on game)",
            "6 - it's worth every cent",
            "You do not survive the journey to California",
            "Quit the game.",
            "End Game",
            "You have survived the Donner Party's journey to California!",
        }
        self.texts = set()

    def GoToURL(self, url):
        self.texts = set()
        self.driver.get(url)
        time.sleep(0.5)

    def GetText(self):
        div_elements = self.driver.find_elements_by_css_selector("div")
        text = div_elements[3].text
        return text

    def GetLinks(self):
        return self.driver.find_elements_by_css_selector("a")

    def GoBack(self):
        self.GetLinks()[0].click()
        time.sleep(0.2)

    def ClickAction(self, links, action_num):
        links[action_num + 4].click()
        time.sleep(0.2)

    def GetActions(self):
        return [link.text for link in self.GetLinks()[4:]]

    def NumActions(self):
        return len(self.GetLinks()) - 4

    def BuildTreeHelper(self, parent_story, action_num, depth, old_actions):
        depth += 1
        action_result = {}

        action = old_actions[action_num]
        print("Action is ", repr(action))
        action_result["action"] = action

        links = self.GetLinks()
        if action_num + 4 >= len(links):
            return None

        self.ClickAction(links, action_num)
        result = self.GetText()
        if result == parent_story or result in self.texts:
            self.GoBack()
            return None

        self.texts.add(result)
        print(len(self.texts))

        action_result["result"] = result

        actions = self.GetActions()
        action_result["action_results"] = []

        for i, action in enumerate(actions):
            if actions[i] not in self.end_actions:
                sub_action_result = self.BuildTreeHelper(result, i, depth, actions)
                if action_result is not None:
                    action_result["action_results"].append(sub_action_result)

        self.GoBack()
        return action_result

    def BuildStoryTree(self, url):
        scraper.GoToURL(url)
        text = scraper.GetText()
        actions = self.GetActions()
        story_dict = {}
        story_dict["tree_id"] = url
        story_dict["context"] = ""
        story_dict["first_story_block"] = text
        story_dict["action_results"] = []

        for i, action in enumerate(actions):
            if action not in self.end_actions:
                action_result = self.BuildTreeHelper(text, i, 0, actions)
                if action_result is not None:
                    story_dict["action_results"].append(action_result)
            else:
                print("done")

        return story_dict


def save_tree(tree, filename):
    with open(filename, "w") as fp:
        json.dump(tree, fp)


scraper = Scraper()

urls = [
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=11144",
    "http://chooseyourstory.com/story/viewer/default.aspx?StoryId=11545",
	"http://chooseyourstory.com/story/viewer/default.aspx?StoryId=60657",
	"http://chooseyourstory.com/story/viewer/default.aspx?StoryId=4720",
	"http://chooseyourstory.com/story/viewer/default.aspx?StoryId=11413",
	"http://chooseyourstory.com/story/viewer/default.aspx?StoryId=17148",
	"http://chooseyourstory.com/story/viewer/default.aspx?StoryId=45225",
	"http://chooseyourstory.com/story/viewer/default.aspx?StoryId=12165",
	"http://chooseyourstory.com/story/viewer/default.aspx?StoryId=10103",
]

for i in range(4, len(urls)):
    print("****** Extracting Adventure ", urls[i], " ***********")
    tree = scraper.BuildStoryTree(urls[i])
    save_tree(tree, "stories/story" + str(i) + ".json")

print("done")
