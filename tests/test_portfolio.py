from html.parser import HTMLParser
import unittest

from server import app


class PageStructure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.sections = []
        self.links = []
        self.scripts = []
        self.experience_bullet_counts = []
        self._in_experience = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if "data-section" in attrs:
            self.sections.append(attrs["data-section"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag == "script":
            self.scripts.append(attrs.get("src", ""))
        if tag == "details" and "experience-item" in attrs.get("class", "").split():
            self._in_experience = True
            self.experience_bullet_counts.append(0)
        if tag == "li" and self._in_experience:
            self.experience_bullet_counts[-1] += 1

    def handle_endtag(self, tag):
        if tag == "details" and self._in_experience:
            self._in_experience = False


class PortfolioTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.response = self.client.get("/")
        self.html = self.response.get_data(as_text=True)
        self.page = PageStructure()
        self.page.feed(self.html)

    def test_document_structure_and_unique_ids(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.page.sections, [
            "about", "ventings", "experience", "projects", "research", "skills", "contact"
        ])
        self.assertEqual(len(self.page.ids), len(set(self.page.ids)))
        self.assertEqual(self.page.scripts, ["./static/portfolio.js"])

    def test_about_is_visible_and_remaining_sections_are_collapsible(self):
        self.assertNotIn('class="wordmark"', self.html)
        self.assertNotIn('<nav', self.html)
        self.assertIn('<p class="intro-lead">Software Engineer</p>', self.html)
        self.assertNotIn("I build reliable software systems", self.html)
        self.assertNotIn("Academic record", self.html)
        self.assertNotIn("3.94 / 4.0", self.html)
        for section in ["ventings", "experience", "work", "research", "skills", "contact"]:
            self.assertIn(
                f'<details class="page-section collapsible-section',
                self.html,
            )
            self.assertIn(f'id="{section}"', self.html)

    def test_content_includes_all_experience_roles(self):
        for role in ["NVIDIA", "Schneider Electric", "Teaching Assistant",
                     "Sophomore Research Assistant", "AI Research Intern",
                     "Software Ecosystems Research Intern", "Power Changes Lives"]:
            self.assertIn(role, self.html)
        self.assertIn("35%", self.html)
        self.assertEqual(len(self.page.experience_bullet_counts), 7)
        self.assertEqual(self.page.experience_bullet_counts[0], 5)
        self.assertTrue(all(count >= 3 for count in self.page.experience_bullet_counts))
        self.assertIn("PostgreSQL advisory locks", self.html)
        self.assertIn("directory-group membership", self.html)
        self.assertIn("disk telemetry", self.html)
        self.assertIn("HiveMind", self.html)
        self.assertIn("40+ reviewed pull requests", self.html)
        self.assertIn("World of Code dataset", self.html)

    def test_projects_and_credentials_remain_available(self):
        for title in ["MCP Agent Stack", "Tandem", "CUDA Route Optimization", "AfroByte",
                      "Impulse", "MyMeal", "Mutual Fund Calculator", "Clara",
                      "Real-Time Chat", "Mighty-Med-Equip", "Foundations of AI Security"]:
            self.assertIn(title, self.html)
        self.assertIn("Random Forest", self.html)
        self.assertNotIn("CNN-based", self.html)

    def test_source_conflicts_not_published_as_facts(self):
        self.assertNotIn("347-5108", self.html)
        self.assertNotIn("Incoming", self.html)
        self.assertNotIn("beginning in 2027", self.html)
        self.assertIn("closed-set", self.html)

    def test_contact_and_proof_links_preserved(self):
        self.assertIn("mailto:hiruyworku00@gmail.com", self.page.links)
        sharepoint_links = {link for link in self.page.links if "sharepoint.com" in link}
        self.assertEqual(len(sharepoint_links), 2)
        self.assertIn("https://github.com/HiruyWorku/Tandem-Senior_IS-", self.page.links)
        self.assertIn("https://x.com/hiruy_w", self.page.links)
        self.assertIn("https://www.instagram.com/hiruy_00/", self.page.links)
        self.assertIn('action="/submit_form"', self.html)
        self.assertIn("usp=sharing", self.html)

    def test_static_images_remain_available(self):
        assets = [
            "plates/tandem.webp", "plates/afrobyte.webp", "about/profile.webp", "about/nvidia-event.jpg",
            "about/tandem-poster.jpg", "about/tandem-defense.jpg"
        ]
        for asset in assets:
            with self.client.get(f"/static/assets/{asset}") as response:
                self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
