"""Local unit tests. Network paths use fixtures/mocks, never claim live availability."""
import copy
import datetime as dt
import io
import json
from pathlib import Path
import socket
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import asset_fetch as af
import prepare_texture as pt
import validate_package as vp


def png_bytes():
    stream = io.BytesIO(); Image.new("RGBA", (4, 4), (255, 255, 255, 128)).save(stream, format="PNG"); return stream.getvalue()

def make_zip(members):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as z:
        for name, data in members: z.writestr(name, data)
    return stream.getvalue()

def evidence():
    return {"asset_page": "https://opengameart.org/content/particle-pack-80-sprites", "creator": "Test fixture, not an actual download",
            "license": "CC0-1.0", "license_evidence_url": "https://opengameart.org/content/particle-pack-80-sprites",
            "verified_at": dt.date.today().isoformat(), "download_url": "https://opengameart.org/sites/default/files/kenney_particlePack.zip",
            "reviewer": "unit_test", "review_notes": "Synthetic fixture only; does not attest actual newly downloaded rights.", "review_complete": True}

class AcquisitionTests(unittest.TestCase):
    def test_host_and_credentials(self):
        af.validate_url("https://opengameart.org/sites/default/files/a.png")
        for url in ["http://opengameart.org/a", "https://127.0.0.1/a", "https://opengameart.org.evil.test/a", "https://x:y@opengameart.org/a", "https://opengameart.org:444/a"]:
            with self.subTest(url=url), self.assertRaises(ValueError): af.validate_url(url)
    def test_private_dns_rejected(self):
        with patch.object(socket, "getaddrinfo", return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]):
            with self.assertRaises(ValueError): af.validate_url("https://opengameart.org/a", resolve=True)
    def test_evidence_gate(self):
        af.validate_evidence(evidence())
        for change in [{"review_complete":False}, {"license":"CC-BY-4.0"}, {"creator":""}, {"verified_at":"2000-01-01"}]:
            bad = evidence(); bad.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError): af.validate_evidence(bad)
    def test_paths(self):
        for name in ["../a.png", "/a.png", "C:/a.png", "a\\b.png", "CON.png", "a/../b.png"]:
            with self.subTest(name=name), self.assertRaises(ValueError): af.safe_member(name)
    def test_extract_images_not_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)/"files"
            records = af.safe_extract_zip(make_zip([("img/a.png",png_bytes()),("LICENSE.txt",b"fixture"),("evil.py",b"raise RuntimeError")]),target)
            self.assertEqual(len(records),2); self.assertFalse((target/"evil.py").exists())
    def test_zip_traversal_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"files"
            with self.assertRaises(ValueError): af.safe_extract_zip(make_zip([("../escape.png",png_bytes())]),target)
            self.assertFalse(target.exists())
    def test_symlink_rejected(self):
        info=zipfile.ZipInfo("link.png"); info.create_system=3; info.external_attr=(stat.S_IFLNK|0o777)<<16
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): af.safe_extract_zip(make_zip([(info,b"/etc/passwd")]),Path(tmp)/"files")
    def test_case_collision(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): af.safe_extract_zip(make_zip([("A.png",png_bytes()),("a.png",png_bytes())]),Path(tmp)/"files")
    def test_invalid_image_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): af.safe_extract_zip(make_zip([("image.png",b"<html>not image</html>")]),Path(tmp)/"files")
            self.assertFalse((Path(tmp)/"files").exists())
    def test_download_manifest_with_mocked_network(self):
        content=make_zip([("a.png",png_bytes())])
        with tempfile.TemporaryDirectory() as tmp, patch.object(af,"fetch",return_value=(content,evidence()["download_url"],"application/zip")):
            target=Path(tmp)/"download"
            result=af.download(evidence(),target)
            self.assertEqual(result["original_sha256"],af.sha256(content))
            self.assertEqual(result["roblox_import"]["status"],"not_imported")
            self.assertTrue((target/"files/a.png").is_file())
            with self.assertRaises(ValueError): af.download(evidence(),target)
    def test_html_download_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(af,"fetch",return_value=(b"<html>login</html>",evidence()["download_url"],"text/html")):
            target=Path(tmp)/"download"
            with self.assertRaises(ValueError): af.download(evidence(),target)
            self.assertFalse(target.exists()); self.assertEqual(list(Path(tmp).iterdir()),[])
    def test_html_link_discovery_fixture(self):
        p=af.LinkParser(); p.feed('<a href="/a.zip">file</a><script>bad()</script>')
        self.assertEqual(p.links,["/a.zip"])

class TextureTests(unittest.TestCase):
    def test_preserve_alpha_and_aspect(self):
        im=Image.new("RGBA",(4,2),(20,30,40,128)); out=pt.normalize(im,8,pixel=True)
        self.assertEqual(out.size,(8,8)); self.assertEqual(out.getpixel((0,0))[3],0)
        self.assertEqual(out.getpixel((4,4))[3],128)
    def test_explicit_luminance_and_white(self):
        im=Image.new("RGBA",(2,2),(128,128,128,128)); out=pt.normalize(im,2,"luminance",True)
        self.assertEqual(out.getpixel((0,0))[:3],(255,255,255)); self.assertEqual(out.getpixel((0,0))[3],64)
    def test_atlas_order(self):
        frames=[Image.new("RGBA",(2,2),(i,0,0,255)) for i in (10,20,30,40)]
        out=pt.pack(frames,2,2)
        self.assertEqual([out.getpixel(p)[0] for p in [(0,0),(2,0),(0,2),(2,2)]],[10,20,30,40])
    def test_atlas_mismatch(self):
        with self.assertRaises(ValueError): pt.pack([Image.new("RGBA",(2,2))],2,2)
        with self.assertRaises(ValueError): pt.pack([Image.new("RGBA",(2,2)),Image.new("RGBA",(3,2))],2,1)
    def test_save_manifest_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"mask.png"; im=Image.new("RGBA",(2,2))
            result=pt.save(im,out,{"operation":"fixture"})
            self.assertEqual(result["sha256"],pt.digest(out)); self.assertTrue(out.with_suffix(".png.meta.json").exists())
            with self.assertRaises(ValueError): pt.save(im,out,{})

class PlanTests(unittest.TestCase):
    def setUp(self):
        self.spec=json.loads((ROOT/"templates/specs/effect-spec.example.json").read_text())
        self.schema=json.loads((ROOT/"templates/specs/effect-spec.schema.json").read_text())
    def test_good_plan(self): vp.validate_spec(self.spec,self.schema)
    def test_critical_cannot_be_disabled(self):
        self.spec["quality_tiers"]["low"]["disabled_layers"]=["contact"]
        with self.assertRaises(ValueError): vp.validate_spec(self.spec,self.schema)
    def test_tail_not_truncated(self):
        self.spec["cleanup"]["maximum_seconds"]=0.1
        with self.assertRaises(ValueError): vp.validate_spec(self.spec,self.schema)
    def test_no_false_validated_assets(self):
        self.spec["status"]="validated"
        with self.assertRaises(ValueError): vp.validate_spec(self.spec,self.schema)
    def test_duplicate_layer(self):
        self.spec["layers"].append(copy.deepcopy(self.spec["layers"][0]))
        with self.assertRaises(ValueError): vp.validate_spec(self.spec,self.schema)
    def test_unmapped_texture(self):
        self.spec["layers"][0]["texture_role"]="not_in_manifest"
        with self.assertRaises(ValueError): vp.validate_spec(self.spec,self.schema)
    def test_package(self): self.assertEqual(vp.validate_package(ROOT)["status"],"passed")

if __name__ == "__main__": unittest.main()
