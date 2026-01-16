const fetch = require('node-fetch');

console.log('🧪 Testing WhatsApp Integration Setup...\n');

async function testSetup() {
    const backendUrl = 'http://127.0.0.1:8000';
    
    // Test 1: Backend connectivity
    console.log('1️⃣ Testing backend connectivity...');
    try {
        const response = await fetch(`${backendUrl}/tasks`);
        if (response.ok) {
            const tasks = await response.json();
            console.log(`   ✅ Backend is running at ${backendUrl}`);
            console.log(`   📊 Current tasks in database: ${tasks.length}`);
        } else {
            console.log(`   ❌ Backend returned status: ${response.status}`);
            process.exit(1);
        }
    } catch (error) {
        console.log(`   ❌ Cannot connect to backend: ${error.message}`);
        console.log(`   💡 Make sure backend is running: cd backend && python run_server.py`);
        process.exit(1);
    }
    
    // Test 2: AI extraction endpoint
    console.log('\n2️⃣ Testing AI deadline extraction...');
    try {
        const response = await fetch(`${backendUrl}/extract_deadline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'Meeting tomorrow at 3 PM' })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log(`   ✅ AI extraction is working`);
            if (result.deadlines && result.deadlines.length > 0) {
                console.log(`   📝 Test extraction: "${result.deadlines[0].task}" on ${result.deadlines[0].date}`);
            }
        } else {
            console.log(`   ⚠️  AI extraction returned status: ${response.status}`);
        }
    } catch (error) {
        console.log(`   ⚠️  AI extraction test failed: ${error.message}`);
    }
    
    // Test 3: Dependencies check
    console.log('\n3️⃣ Checking dependencies...');
    try {
        require('whatsapp-web.js');
        console.log('   ✅ whatsapp-web.js installed');
        
        require('qrcode-terminal');
        console.log('   ✅ qrcode-terminal installed');
        
        require('dotenv');
        console.log('   ✅ dotenv installed');
    } catch (error) {
        console.log(`   ❌ Missing dependency: ${error.message}`);
        console.log(`   💡 Run: npm install`);
        process.exit(1);
    }
    
    console.log('\n✅ All tests passed! Ready to start WhatsApp monitor.\n');
    console.log('📱 Next step: Run "npm start" to start the monitor and scan QR code\n');
}

testSetup().catch(console.error);
