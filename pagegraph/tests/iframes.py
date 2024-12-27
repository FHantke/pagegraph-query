from __future__ import annotations

from typing import TYPE_CHECKING

from pagegraph.urls import security_origin_from_url
from pagegraph.tests import PageGraphBaseTestClass

if TYPE_CHECKING:
    from pagegraph.types import Url


ABOUT_BLANK_URL = "about:blank"
FRAME_URL = "assets/frames/blank-frame.html"


class IFramesBasicTestCase(PageGraphBaseTestClass):
    NAME = "iframes-about_blank"

    def test_num_iframes(self) -> None:
        frame_nodes = self.graph.iframe_nodes()
        self.assertEqual(len(frame_nodes), 1)

    def test_num_domroots(self) -> None:
        frame_nodes = self.graph.iframe_nodes()
        iframe_node = frame_nodes[0]
        domroot_nodes = iframe_node.child_domroot_nodes()
        self.assertEqual(len(domroot_nodes), 2)

        automatic_domroot = None
        final_domroot = None
        for domroot_node in domroot_nodes:
            if domroot_node.is_init_domroot():
                automatic_domroot = domroot_node
            else:
                final_domroot = domroot_node
        self.assertIsNotNone(automatic_domroot)
        self.assertEqual(automatic_domroot.url(), ABOUT_BLANK_URL)
        self.assertTrue(automatic_domroot.is_local_domroot())

        self.assertIsNotNone(final_domroot)
        self.assertEqual(final_domroot.url(), ABOUT_BLANK_URL)
        self.assertTrue(final_domroot.is_local_domroot())

        self.assertTrue(
            automatic_domroot.timestamp() <= final_domroot.timestamp())
        self.assertTrue(automatic_domroot.id() < final_domroot.id())


class IFramesNavigationTestCase(PageGraphBaseTestClass):
    NAME = "iframes-navigation"

    def test_num_iframes(self) -> None:
        frame_nodes = self.graph.iframe_nodes()
        self.assertEqual(len(frame_nodes), 1)

    def test_parser_generated_frame(self) -> None:
        frame_nodes = self.graph.iframe_nodes()
        iframe_node = frame_nodes[0]

        # There should be three child documents in the iframe:
        #  1. the initial about:blank frame
        #  2. the temporary about:blank one, created as part of the navigation
        #     process
        #  3. the navigated to "/assets/frames/blank-frame.html" frame.
        domroot_nodes = iframe_node.child_domroot_nodes()
        self.assertEqual(len(domroot_nodes), 3)

        init_domroot = None
        about_blank_domroot = None
        dest_domroot = None
        for node in domroot_nodes:
            if FRAME_URL in node.url():
                dest_domroot = node
            elif node.url() == ABOUT_BLANK_URL:
                if node.is_init_domroot():
                    init_domroot = node
                else:
                    about_blank_domroot = node
        self.assertIsNotNone(init_domroot)
        self.assertIsNotNone(about_blank_domroot)
        self.assertIsNotNone(dest_domroot)

        # Now check to make sure the nodes occurred in the expected order.
        self.assertTrue(
            init_domroot.timestamp() <= about_blank_domroot.timestamp())
        self.assertTrue(
            about_blank_domroot.timestamp() <= dest_domroot.timestamp())

        self.assertTrue(init_domroot.id() < about_blank_domroot.id())
        self.assertTrue(about_blank_domroot.id() < dest_domroot.id())


class IFramesSecurityOriginsTestCase(PageGraphBaseTestClass):
    NAME = "iframes-security_origin"

    def graph_security_origin(self) -> Url:
        return security_origin_from_url(self.graph.url)

    def test_top_frame_security_origin(self) -> None:
        top_level_frame = self.graph.get_elements_by_id("frame1")
        self.assertEqual(len(top_level_frame), 1)
        domroot = top_level_frame[0].domroot_node()
        self.assertIsNotNone(domroot)
        self.assertEqual(self.graph_security_origin(), domroot.security_origin())

    def test_srcdoc_frame_security_origin(self) -> None:
        srcdoc_frame = self.graph.get_elements_by_id("frame2")
        self.assertEqual(len(srcdoc_frame), 1)
        domroot = srcdoc_frame[0].domroot_node()
        self.assertIsNotNone(domroot)
        self.assertEqual(self.graph_security_origin(), domroot.security_origin())

    def test_remote_frame_security_origin(self) -> None:
        remote_frame = self.graph.get_elements_by_id("frame3")
        self.assertEqual(len(remote_frame), 1)
        domroot = remote_frame[0].domroot_node()
        self.assertIsNotNone(domroot)
        self.assertNotEqual(self.graph_security_origin(), domroot.security_origin())

    def test_aboutblank_frame_security_origin(self) -> None:
        blank_frame = self.graph.get_elements_by_id("frame4")
        self.assertEqual(len(blank_frame), 1)
        domroot = blank_frame[0].domroot_node()
        self.assertIsNotNone(domroot)
        self.assertEqual(self.graph_security_origin(), domroot.security_origin())


class IFramesSubDocumentTestCase(PageGraphBaseTestClass):
    NAME = "iframes-sub_document"

    def test_num_iframes(self) -> None:
        frame_nodes = self.graph.iframe_nodes()
        self.assertEqual(len(frame_nodes), 1)

    def test_text_frame_with_src(self) -> None:
        frame_nodes = self.graph.iframe_nodes()
        iframe_node = frame_nodes[0]

        domroot_nodes = iframe_node.child_domroot_nodes()
        self.assertEqual(len(domroot_nodes), 2)

        init_domroot = None
        dest_domroot = None
        for node in domroot_nodes:
            if ABOUT_BLANK_URL in node.url():
                init_domroot = node
            elif FRAME_URL in node.url():
                dest_domroot = node

        self.assertIsNotNone(init_domroot)
        self.assertIsNotNone(dest_domroot)
        self.assertTrue(init_domroot.timestamp() <= dest_domroot.timestamp())
        self.assertTrue(init_domroot.id() < dest_domroot.id())


class IFramesIsSecurityOriginInheritingTestCase(PageGraphBaseTestClass):
    NAME = "iframes-is_security_origin_inheriting"

    def test_initial_about_blank(self) -> None:
        frame = self.graph.get_elements_by_id("frame1")[0]
        self.assertTrue(frame.is_security_origin_inheriting())

    def test_initial_remote_origin(self) -> None:
        frame = self.graph.get_elements_by_id("frame2")[0]
        self.assertFalse(frame.is_security_origin_inheriting())

    def test_nested_about_blank(self) -> None:
        frame = self.graph.get_elements_by_id("frame3")[0]
        self.assertTrue(frame.is_security_origin_inheriting())

    def test_nested_remote_origin(self) -> None:
        frame = self.graph.get_elements_by_id("frame4")[0]
        self.assertFalse(frame.is_security_origin_inheriting())


class IFramesIsThirdPartyToRootTestCase(PageGraphBaseTestClass):
    NAME = "iframes-is_third_party_to_root"

    def test_about_blank_frame(self) -> None:
        frame = self.graph.get_elements_by_id("frame1")[0]
        self.assertFalse(frame.is_third_party_to_root())

    def test_remote_origin_frame(self) -> None:
        frame = self.graph.get_elements_by_id("frame2")[0]
        self.assertTrue(frame.is_third_party_to_root())

    def test_local_origin_frame(self) -> None:
        frame = self.graph.get_elements_by_id("frame3")[0]
        self.assertFalse(frame.is_third_party_to_root())


class IFramesIsTopLevelDOMRootTestCase(PageGraphBaseTestClass):
    NAME = "iframes-is_top_level_domroot"

    def test_initial_about_blank_frame(self) -> None:
        frame = self.graph.get_elements_by_id("frame1")[0]
        domroot_node = frame.domroot_node()
        self.assertFalse(domroot_node.is_top_level_domroot())

    def test_parent_of_initial_about_blank_frame(self) -> None:
        frame = self.graph.get_elements_by_id("frame1")[0]
        domroot_node = frame.execution_context()
        self.assertTrue(domroot_node.is_top_level_domroot())

    def test_nested_injected_iframe(self) -> None:
        frame = self.graph.get_elements_by_id("frame2")[0]
        domroot_node = frame.domroot_node()
        self.assertFalse(domroot_node.is_top_level_domroot())

    def test_nested_srcdoc_iframe(self) -> None:
        frame = self.graph.get_elements_by_id("frame3")[0]
        domroot_node = frame.domroot_node()
        self.assertFalse(domroot_node.is_top_level_domroot())
