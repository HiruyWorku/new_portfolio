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
        for role in ["NVIDIA", "Wooster NSBE Chapter", "Schneider Electric", "Teaching Assistant",
                     "Sophomore Research Assistant", "AI Research Intern",
                     "Software Ecosystems Research Intern", "Power Changes Lives"]:
            self.assertIn(role, self.html)
        self.assertIn("35%", self.html)
        self.assertEqual(self.page.experience_bullet_counts, [5, 1, 5, 4, 4, 4, 3, 4])
        for dates in ["May 2026 - Aug 2026", "Aug 2025 - Apr 2026",
                      "May 2025 - Jul 2025", "Sep 2024 - Jun 2025",
                      "Mar 2025 - May 2025", "Jan 2025 - May 2025",
                      "Jun 2024 - Aug 2024"]:
            self.assertIn(f"<time>{dates}</time>", self.html)
        self.assertIn("PostgreSQL advisory locks", self.html)
        self.assertIn("directory-group membership", self.html)
        self.assertIn("disk telemetry", self.html)
        self.assertIn("HiveMind", self.html)
        self.assertIn("40+ reviewed pull requests", self.html)
        self.assertIn("World of Code dataset", self.html)

    def test_about_copy_and_community_placement(self):
        about = self.html.split('id="about"', 1)[1].split('id="experience"', 1)[0]
        self.assertIn("Computer Science and Mathematics", about)
        self.assertIn("cinematography, photography, design, drawing, and prototyping", about)
        self.assertIn("contributing to open source", about)
        self.assertIn("For my senior thesis, I built Tandem", about)
        self.assertNotIn("community-list", about)
        self.assertNotIn("Google Developer Groups", self.html)

    def test_projects_and_credentials_remain_available(self):
        projects = self.html.split('id="work"', 1)[1].split('id="research"', 1)[0]
        featured, earlier = projects.split('<details class="project-archive">', 1)
        featured_titles = ["Tandem", "CUDA Route Optimization", "Mutual Fund Calculator", "Issue Finder"]
        earlier_titles = ["AfroByte", "Impulse", "MyMeal", "Clara", "Real-Time Chat",
                          "Mighty-Med-Equip", "Waymo 2.0", "Doom", "From-Scratch CPU"]
        self.assertEqual(featured.count('class="project-entry"'), 4)
        self.assertEqual(earlier.count('<article>'), 9)
        self.assertTrue(all(f'<h3>{title}</h3>' in featured for title in featured_titles))
        self.assertTrue(all(f'>{title}</a>' in earlier for title in earlier_titles))
        self.assertEqual([featured.find(f'<h3>{title}</h3>') for title in featured_titles],
                         sorted(featured.find(f'<h3>{title}</h3>') for title in featured_titles))
        self.assertEqual([earlier.find(f'>{title}</a>') for title in earlier_titles],
                         sorted(earlier.find(f'>{title}</a>') for title in earlier_titles))
        self.assertIn("Earlier projects", earlier)
        self.assertNotIn("MCP Agent Stack", projects)
        self.assertNotIn("project-image", projects)
        self.assertNotIn("static/assets/plates/", projects)
        self.assertIn("Foundations of AI Security", self.html)
        self.assertIn("Random Forest", self.html)
        self.assertNotIn("CNN-based", self.html)

    def test_source_conflicts_not_published_as_facts(self):
        self.assertNotIn("347-5108", self.html)
        self.assertNotIn("Incoming", self.html)
        self.assertNotIn("beginning in 2027", self.html)
        self.assertIn("closed-set", self.html)

    def test_research_paper_order(self):
        research = self.html.split('id="research"', 1)[1].split('id="skills"', 1)[0]
        titles = ["Real-Time ASL and Speech Communication",
                  "Sparse Paths to Scale", "CUDA-Accelerated Reinforcement Learning"]
        positions = [research.find(title) for title in titles]
        self.assertTrue(all(position >= 0 for position in positions))
        self.assertEqual(positions, sorted(positions))
        self.assertIn("https://drive.google.com/file/d/1jcXWFvobEY6Wdp1hBDYdFwgOkDZe6a_k/view?usp=sharing", self.page.links)

    def test_contact_and_proof_links_preserved(self):
        self.assertIn("mailto:hiruyworku00@gmail.com", self.page.links)
        sharepoint_links = {link for link in self.page.links if "sharepoint.com" in link}
        self.assertEqual(len(sharepoint_links), 2)
        for link in [
            "https://github.com/HiruyWorku/Tandem-Senior_IS",
            "https://github.com/HiruyWorku/RL-Maze-Reinforcement-Learning-for-Route-Optimization",
            "https://github.com/HiruyWorku/Mutual-Fund-Calculator_fork",
            "https://github.com/HiruyWorku/issue-finder",
            "https://github.com/HiruyWorku/A.F.R.O.-Byte",
            "https://github.com/HiruyWorku/Impulse",
            "https://github.com/HiruyWorku/My_Meal",
            "https://github.com/HiruyWorku/Clara",
            "https://github.com/HiruyWorku/chatapp",
            "https://github.com/HiruyWorku/Might-Med-Equip",
            "https://github.com/HiruyWorku/Waymo2.0",
            "https://github.com/HiruyWorku/Doom",
            "https://drive.google.com/file/d/197rdKS_6SiAsw9vPyZJESEY-d-5qj5wZ/view?usp=sharing",
        ]:
            self.assertIn(link, self.page.links)
        self.assertIn("https://x.com/hiruy_w", self.page.links)
        self.assertIn("https://www.instagram.com/hiruy_00/", self.page.links)
        self.assertIn("https://scholar.google.com/citations?user=DGYUamAAAAAJ&hl=en", self.page.links)
        self.assertIn("https://letterboxd.com/hiruy_worku/", self.page.links)
        self.assertIn('action="/submit_form"', self.html)
        self.assertIn("usp=sharing", self.html)

    def test_static_images_remain_available(self):
        assets = [
            "about/profile.webp", "about/nvidia-event.jpg",
            "about/tandem-poster.jpg", "about/tandem-defense.jpg"
        ]
        for asset in assets:
            with self.client.get(f"/static/assets/{asset}") as response:
                self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
