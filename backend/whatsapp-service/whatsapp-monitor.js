const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fetch = require('node-fetch');
const config = require('./whatsapp-config');

console.log('🚀 Starting WhatsApp Deadline Monitor...');
console.log(`📡 Backend URL: ${config.backendUrl}`);

// Initialize WhatsApp client with persistent session
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './.wwebjs_auth'
    }),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// Track processed messages to avoid duplicates
const processedMessages = new Set();

// Generate QR code for first-time authentication
client.on('qr', (qr) => {
    console.log('\n📱 Scan this QR code with WhatsApp:\n');
    qrcode.generate(qr, { small: true });
    console.log('\n👆 Open WhatsApp on your phone → Settings → Linked Devices → Link a Device\n');
});

// Client is ready
client.on('ready', () => {
    console.log('✅ WhatsApp monitoring is now ACTIVE!');
    console.log('📨 Listening for deadline-related messages...\n');
});

// Handle authentication
client.on('authenticated', () => {
    console.log('🔐 Authentication successful!');
});

// Handle authentication failure
client.on('auth_failure', (msg) => {
    console.error('❌ Authentication failed:', msg);
    console.log('💡 Try deleting .wwebjs_auth folder and scanning QR code again');
});

// Handle disconnection
client.on('disconnected', (reason) => {
    console.log('⚠️  WhatsApp disconnected:', reason);
    console.log('🔄 Attempting to reconnect...');
});

// Listen to all incoming messages
client.on('message', async (message) => {
    try {
        // Avoid processing the same message twice
        if (processedMessages.has(message.id._serialized)) {
            return;
        }
        processedMessages.add(message.id._serialized);
        
        // Clean up old processed messages (keep last 1000)
        if (processedMessages.size > 1000) {
            const toDelete = Array.from(processedMessages).slice(0, 100);
            toDelete.forEach(id => processedMessages.delete(id));
        }
        
        const text = message.body;
        
        // Get message metadata
        const contact = await message.getContact();
        const chat = await message.getChat();
        const senderName = contact.pushname || contact.name || contact.number;
        const chatName = chat.name || senderName;
        const isGroup = chat.isGroup;
        
        // Apply message filters
        if (!shouldProcessMessage(text, message, isGroup, senderName)) {
            return;
        }
        
        // Log message if enabled
        if (config.logging.logAllMessages) {
            console.log(`📨 Message from ${senderName} in ${chatName}: ${text.substring(0, 50)}...`);
        }
        
        // Check if message contains deadline keywords
        if (containsDeadlineKeywords(text)) {
            console.log(`\n🔍 Potential deadline detected!`);
            console.log(`   From: ${senderName}`);
            console.log(`   Chat: ${chatName} ${isGroup ? '(Group)' : '(Personal)'}`);
            console.log(`   Message: "${text.substring(0, 100)}${text.length > 100 ? '...' : ''}"`);
            
            // Extract deadline using AI
            await extractAndStoreDeadline(text, senderName, chatName, isGroup);
        }
        
    } catch (error) {
        if (config.logging.logErrors) {
            console.error('❌ Error processing message:', error.message);
        }
    }
});

// Check if message should be processed
function shouldProcessMessage(text, message, isGroup, senderName) {
    const filter = config.messageFilter;
    const chatFilterConfig = config.chatFilter;
    
    // Check message length
    if (text.length < filter.minLength || text.length > filter.maxLength) {
        return false;
    }
    
    // Ignore messages from self
    if (filter.ignoreSelf && message.fromMe) {
        return false;
    }
    
    // Check chat type filter
    if (isGroup && !chatFilterConfig.monitorGroups) {
        return false;
    }
    if (!isGroup && !chatFilterConfig.monitorPersonal) {
        return false;
    }
    
    // Check if keywords are required
    if (filter.requireKeywords && !containsDeadlineKeywords(text)) {
        return false;
    }
    
    return true;
}

// Check if text contains deadline-related keywords
function containsDeadlineKeywords(text) {
    const lowerText = text.toLowerCase();
    return config.deadlineKeywords.some(keyword => 
        lowerText.includes(keyword.toLowerCase())
    );
}

// Extract deadline using backend AI and store in database
async function extractAndStoreDeadline(text, sender, chatName, isGroup) {
    try {
        // Step 1: Extract deadline using AI
        console.log('   🤖 Sending to AI for extraction...');
        
        const extractResponse = await fetch(`${config.backendUrl}/extract_deadline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        
        if (!extractResponse.ok) {
            throw new Error(`AI extraction failed: ${extractResponse.status}`);
        }
        
        const { deadlines } = await extractResponse.json();
        
        if (!deadlines || deadlines.length === 0) {
            console.log('   ℹ️  No deadlines found in message\n');
            return;
        }
        
        // Step 2: Create tasks for each detected deadline
        for (const deadline of deadlines) {
            if (!deadline.task || !deadline.date) {
                continue;
            }
            
            const source = `WhatsApp - ${chatName}${isGroup ? ' (Group)' : ''}`;
            
            console.log(`   ✅ Deadline extracted:`);
            console.log(`      Task: ${deadline.task}`);
            console.log(`      Due: ${deadline.date}`);
            console.log(`      Source: ${source}`);
            
            // Create task in database
            const createResponse = await fetch(`${config.backendUrl}/tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    summary: deadline.task,
                    deadline: deadline.date,
                    source: source,
                    alert_status: 'pending'
                })
            });
            
            if (createResponse.ok) {
                const task = await createResponse.json();
                console.log(`   💾 Task created with ID: ${task.id}`);
                
                if (config.logging.logDeadlines) {
                    console.log(`   📱 Task will appear in app automatically!\n`);
                }
            } else {
                console.error(`   ❌ Failed to create task: ${createResponse.status}\n`);
            }
        }
        
    } catch (error) {
        if (config.logging.logErrors) {
            console.error(`   ❌ Error in deadline extraction: ${error.message}\n`);
        }
    }
}

// Initialize the client
console.log('🔄 Initializing WhatsApp client...\n');
client.initialize();

// Handle process termination
process.on('SIGINT', async () => {
    console.log('\n\n🛑 Shutting down WhatsApp monitor...');
    await client.destroy();
    console.log('✅ Cleanup complete. Goodbye!\n');
    process.exit(0);
});

// Keep process alive
process.on('uncaughtException', (error) => {
    console.error('❌ Uncaught exception:', error);
    console.log('🔄 Monitor will continue running...\n');
});
