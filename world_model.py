class WorldModel:
    def __init__(self):
        self.story_context = {
            "plot_summary": "",
            "characters": {},
            "events": [],
            "theme": "",
            "scene_summaries": [],
            "locations": {},
            "objects": {},
            "timeline": []
        }
        self.previous_scene = None

    def init_world_model_from_spec(self, spec_dict):
        self.story_context['theme'] = spec_dict.get('Themes', "")
        characters = spec_dict.get('Characters', '').split(',')
        for char in characters:
            char = char.strip()
            if char:
                self.story_context['characters'][char] = {
                    'description': '',
                    'relationships': [],
                    'motivation': ''
                }

    def add_event(self, event_summary):
         self.story_context['events'].append(event_summary)

    def add_scene_summary(self, scene_summary):
        self.story_context['scene_summaries'].append(scene_summary)

    def get_previous_scene_summary(self):
         return self.story_context['scene_summaries'][-1] if self.story_context['scene_summaries'] else None

    def get_previous_scene(self):
        return self.previous_scene

    def add_previous_scene(self, scene):
        self.previous_scene = scene
