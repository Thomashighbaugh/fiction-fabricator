# /home/tlh/fiction-fabricator/plan.py
import re
import json
from loguru import logger


class Plan:
    @staticmethod
    def split_by_act(original_plan):
        """Splits a plan string into acts based on the 'Act' keyword.

        Args:
            original_plan (str): The plan string to split.

        Returns:
             list: A list of act strings.
        """
        acts = re.split(r"\n\s{0,5}?Act ", original_plan)
        acts = [text.strip() for text in acts[1:] if (text and (len(text.split()) > 3))]
        if len(acts) == 4:
            acts = acts[1:]
        elif len(acts) != 3:
            print("Fail: split_by_act, attempt 1", original_plan)
            acts = original_plan.split("Act ")
            if len(acts) == 4:
                acts = acts[-3:]
            elif len(acts) != 3:
                print("Fail: split_by_act, attempt 2", original_plan)
                return []

        if acts[0].startswith("Act "):
            acts = [acts[0]] + ["Act " + act for act in acts[1:]]
        else:
            acts = ["Act " + act for act in acts[:]]
        return acts

    @staticmethod
    def parse_act_chapters(act):
        """Parses an act string into a dictionary containing the act description and chapters.

        Args:
            act (str): The act string to parse.

         Returns:
            dict: A dictionary with keys 'act_descr' and 'chapters'.
        """
        act = act.strip()
        act_parts = re.split(
            r"\n\s*Chapter\s*\d+\s*:\s*", act
        )  # split by "Chapter <number>: "
        act_descr = act_parts[0].strip()
        chapters = [part.strip() for part in act_parts[1:] if part.strip()]

        return {"act_descr": act_descr, "chapters": chapters}

    @staticmethod
    def parse_act(act):
        """Parses an act string into a dictionary containing the act description and chapters, or an act plan

        Args:
            act (str): The act string to parse.

         Returns:
            dict: A dictionary with keys 'act_descr' and 'chapters' or a dict with 'act_descr' and an empty chapter list.
        """
        act = act.strip()
        if re.search(r"\n\s*Chapter\s*\d+\s*:\s*", act):
            return Plan.parse_act_chapters(act)
        return {"act_descr": act, "chapters": []}

    @staticmethod
    def parse_text_plan(text_plan):
        """Parses a text plan string into a structured list of act dictionaries.

        Args:
            text_plan (str): The plan string to parse.

        Returns:
            list: A list of dictionaries, each representing an act.
        """
        acts = Plan.split_by_act(text_plan)
        if not acts:
            return []
        plan = [Plan.parse_act(act) for act in acts if act]
        # Remove any acts that do not have an act description
        plan = [act for act in plan if act["act_descr"]]
        return plan

    @staticmethod
    def normalize_text_plan(text_plan):
        """Normalizes a text plan by parsing it and then converting it back to a string.

        Args:
            text_plan (str): The plan string to normalize.

        Returns:
             str: The normalized plan string.
        """
        plan = Plan.parse_text_plan(text_plan)
        text_plan = Plan.plan_2_str(plan)
        return text_plan

    @staticmethod
    def act_2_str(plan, act_num):
        """Converts a specific act within a plan to a formatted string.

        Args:
            plan (list): The list of act dictionaries.
            act_num (int): The act number to convert.

         Returns:
             tuple: A tuple containing the formatted act string and list of chapter numbers.
        """
        text_plan = ""
        chs = []
        ch_num = 1
        for i, act in enumerate(plan):
            if isinstance(act, str):
                text_plan = plan
                return text_plan.strip(), chs
            act_descr = act["act_descr"] + "\n"
            if not re.search(r"Act \d", act_descr[0:50]):
                act_descr = f"Act {i+1}:\n" + act_descr
            for chapter in act["chapters"]:
                if (i + 1) == act_num:
                    act_descr += f"- Chapter {ch_num}: {chapter}\n"
                    chs.append(ch_num)
                elif (i + 1) > act_num:
                    return text_plan.strip(), chs
                ch_num += 1
            text_plan += act_descr + "\n"
        return text_plan.strip(), chs

    @staticmethod
    def plan_2_str(plan):
        """Converts a plan (list of acts) to a formatted string.

         Args:
            plan (list): The list of act dictionaries.

        Returns:
            str: The formatted plan string.
        """
        text_plan = ""
        ch_num = 1
        for i, act in enumerate(plan):
            if isinstance(act, str):
                return plan
            elif isinstance(act, dict) and "act_descr" in act and "chapters" in act:
                act_descr = act["act_descr"] + "\n"
                if not re.search(r"Act \d", act_descr[0:50]):
                    act_descr = f"Act {i+1}:\n" + act_descr
                for chapter in act["chapters"]:
                    act_descr += f"- Chapter {ch_num}: {chapter}\n"
                    ch_num += 1
                text_plan += act_descr + "\n"
            else:
                # Handle cases where the act is a dictionary but doesn't have the expected structure
                logger.error(f"Invalid act structure encountered: {act}")
                continue

        return text_plan.strip()

    @staticmethod
    def save_plan(plan, fpath):
        """Saves a plan (list of acts) to a JSON file.

        Args:
            plan (list): The list of act dictionaries.
            fpath (str): The path to save the plan to.
        """
        with open(fpath, "w") as fp:
            json.dump(plan, fp, indent=4)
