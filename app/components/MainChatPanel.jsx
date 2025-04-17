const React = require('react');
const { useState } = React;
const Box = require('@mui/material/Box').default;
const TextField = require('@mui/material/TextField').default;
const Button = require('@mui/material/Button').default;
const List = require('@mui/material/List').default;
const ListItem = require('@mui/material/ListItem').default;
const ListItemText = require('@mui/material/ListItemText').default;
const Paper = require('@mui/material/Paper').default;
const Typography = require('@mui/material/Typography').default;

function MainChatPanel({ messages = [], onSendMessage }) {
    const [userInput, setUserInput] = useState('');
    const chatContainerRef = React.useRef(null);

    // Scroll to bottom when messages update
    React.useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [messages]);


    const handleInputChange = (event) => {
        setUserInput(event.target.value);
    };

    const handleSend = () => {
        if (userInput.trim()) {
            onSendMessage(userInput); // Call the handler passed from App.jsx
            setUserInput(''); // Clear the input field
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Prevent default newline on Enter
            handleSend();
        }
    };

    return React.createElement(Box, { sx: { display: 'flex', flexDirection: 'column', height: '100%', /*bgcolor: 'grey.800'*/ } },
        // Chat Message Display Area
        React.createElement(Box, {
            ref: chatContainerRef,
            sx: {
                flexGrow: 1,
                overflowY: 'auto',
                p: 2,
                mb: 2,
                border: '1px solid grey', // Add border for visibility
                borderRadius: '4px',
                // bgcolor: 'background.paper' // Use theme background
            }
        },
            React.createElement(List, null,
                messages.map((msg, index) =>
                    React.createElement(ListItem, { key: index, sx: { textAlign: msg.role === 'user' ? 'right' : 'left' } },
                        React.createElement(Paper, {
                             elevation: 2,
                             sx: {
                                 p: 1,
                                 display: 'inline-block',
                                 bgcolor: msg.role === 'user' ? 'primary.light' : 'secondary.light',
                                 color: msg.role === 'user' ? 'primary.contrastText' : 'secondary.contrastText',
                                 maxWidth: '80%',
                                 wordWrap: 'break-word' // Ensure long words wrap
                                }
                             },
                            React.createElement(Typography, { variant: 'body1' }, msg.content)
                        )
                    )
                )
            )
        ),
        // Input Area
        React.createElement(Box, { sx: { display: 'flex', p: 1, borderTop: '1px solid grey' } },
            React.createElement(TextField, {
                fullWidth: true,
                variant: 'outlined',
                size: 'small',
                placeholder: 'Chat with Jeff...',
                value: userInput,
                onChange: handleInputChange,
                onKeyPress: handleKeyPress,
                multiline: true, // Allow multiple lines with Shift+Enter
                maxRows: 4 // Limit input height
                // sx: { bgcolor: 'background.paper'} // Use theme background
            }),
            React.createElement(Button, {
                variant: 'contained',
                color: 'primary',
                onClick: handleSend,
                sx: { ml: 1 }
            }, 'Send')
        )
    );
}

exports.default = MainChatPanel; 