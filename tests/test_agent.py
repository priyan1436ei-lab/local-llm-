import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from localcoder.agent import CodingAgent
from localcoder.config import Settings, choose_model
from localcoder.tools import WorkspaceTools, ToolError

class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tools = WorkspaceTools(self.root)

    def test_escape_denied(self):
        for path in ('../escape.txt', '.git/config', '.localcoder/backups/x'):
            with self.assertRaises(ToolError): self.tools.write_file(path, 'x')

    def test_symlink_escape_denied(self):
        with tempfile.TemporaryDirectory() as other:
            try: (self.root/'link').symlink_to(other, target_is_directory=True)
            except OSError: self.skipTest('Symlinks unavailable')
            with self.assertRaises(ToolError): self.tools.write_file('link/x', 'x')

    def test_backup_and_replace(self):
        self.tools.write_file('a.txt', 'before')
        self.tools.replace_in_file('a.txt', 'before', 'after')
        self.assertEqual(self.tools.read_file('a.txt'), 'after')
        backups = list((self.root/'.localcoder/backups').rglob('a.txt'))
        self.assertEqual(backups[0].read_text(), 'before')
        self.assertNotIn('.localcoder', self.tools.list_files())

    def test_command_denied_without_side_effect(self):
        self.tools.approve = lambda _: False
        with self.assertRaises(ToolError): self.tools.run_command('echo unsafe > side.txt')
        self.assertFalse((self.root/'side.txt').exists())

    def test_approved_command_output(self):
        self.tools.approve = lambda _: True
        self.assertIn('exit_code=0',self.tools.run_command('echo localcoder'))

    def test_agent_error_fix_cycle(self):
        a = CodingAgent(self.root, Settings('fake',4096), verbose=False)
        a.client.chat = Mock(side_effect=[
            {'action':'write_file','path':'main.py','content':'print(1)'},
            {'action':'replace_in_file','path':'main.py','find':'missing','replace':'x'},
            {'action':'replace_in_file','path':'main.py','find':'1','replace':'2'},
            {'action':'finish','message':'Implemented; execution not tested'}])
        self.assertIn('Implemented', a.run('create main'))
        self.assertEqual((self.root/'main.py').read_text(),'print(2)')
        messages = a.client.chat.call_args.kwargs['messages']
        self.assertTrue(any('TOOL_ERROR' in m['content'] for m in messages))

    def test_stop_before_write(self):
        a = CodingAgent(self.root, Settings('fake',4096), verbose=False)
        a.cancelled = lambda: True
        a.client.chat = Mock()
        self.assertIn('Stopped',a.run('create'))
        a.client.chat.assert_not_called()

    def test_gpu_profiles(self):
        self.assertEqual(choose_model(4),('qwen2.5-coder:3b',4096))
        self.assertEqual(choose_model(6),('qwen2.5-coder:3b',4096))
        self.assertEqual(choose_model(8),('qwen2.5-coder:7b',4096))

if __name__ == '__main__': unittest.main()
