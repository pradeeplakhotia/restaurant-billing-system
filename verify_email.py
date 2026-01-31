from app import send_email_with_attachment
import unittest
from unittest.mock import MagicMock, patch

class TestEmail(unittest.TestCase):
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        # Mock SMTP instance
        instance = mock_smtp.return_value
        instance.starttls.return_value = None
        instance.login.return_value = None
        instance.send_message.return_value = None
        instance.quit.return_value = None
        
        # Test file path that doesn't exist
        result = send_email_with_attachment('test@example.com', 'Sub', 'Body', 'fake.pdf', 'fake.pdf')
        self.assertEqual(result['status'], 'error')
        self.assertIn('Attachment file not found', result['message'])

        # Create dummy file
        with open('dummy.txt', 'w') as f:
            f.write('content')
            
        result = send_email_with_attachment('test@example.com', 'Sub', 'Body', 'dummy.txt', 'dummy.txt')
        
        import os
        os.remove('dummy.txt')
        
        self.assertEqual(result['status'], 'success')

if __name__ == '__main__':
    unittest.main()
