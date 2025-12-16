<map version="1.0.1">
<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->
<node CREATED="1765854430632" ID="ID_142169591" MODIFIED="1765854727291" TEXT="Readme.mm">
<node CREATED="1765854641269" ID="ID_1420769810" MODIFIED="1765868822469" POSITION="right" TEXT="Work Flows">
<node CREATED="1765854673520" FOLDED="true" ID="ID_1064839152" MODIFIED="1765854851352" TEXT="Web App">
<node CREATED="1765854673539" ID="ID_235425084" MODIFIED="1765854673539" TEXT="# Setup"/>
<node CREATED="1765854673553" FOLDED="true" ID="ID_1990167908" MODIFIED="1765854744178" TEXT="# Development">
<node CREATED="1765854673557" MODIFIED="1765854673557" TEXT="- t1(web-app): npm run dev"/>
<node CREATED="1765854673571" ID="ID_1358968478" MODIFIED="1765854673571" TEXT="- t2(web-app/server): npm start"/>
<node CREATED="1765854673575" LINK="http://localhost:5173/" MODIFIED="1765854673575" TEXT="- open in browser: http://localhost:5173/"/>
</node>
<node CREATED="1765854673586" FOLDED="true" ID="ID_1605324124" MODIFIED="1765854749902" TEXT="# Deployment (Google Cloud Run)">
<node CREATED="1765854673593" MODIFIED="1765854673593" TEXT="- The icon files (ico and png) should be in ./public folder."/>
<node CREATED="1765854673599" MODIFIED="1765854673599" TEXT="- t1 (web-app): gcloud run deploy web-app --source . --platform managed --region asia-south1 --allow-unauthenticated"/>
<node CREATED="1765854673622" LINK="https://web-app-19493053926.asia-south1.run.app/" MODIFIED="1765854673622" TEXT="- App URl: https://web-app-19493053926.asia-south1.run.app/"/>
<node CREATED="1765854673630" LINK="https://console.cloud.google.com/cloud-build/builds?project=planar-leaf-481303-m4" MODIFIED="1765854673630" TEXT="- Build History: https://console.cloud.google.com/cloud-build/builds?project=planar-leaf-481303-m4"/>
</node>
</node>
<node CREATED="1765854707552" ID="ID_1709690881" MODIFIED="1765868824543" TEXT="Windows Application">
<node CREATED="1765854707554" MODIFIED="1765854707554" TEXT="# Setup"/>
<node CREATED="1765854707556" FOLDED="true" ID="ID_1711416165" MODIFIED="1765854727086" TEXT="# Development">
<node CREATED="1765854707557" MODIFIED="1765854707557" TEXT="- t1(web-app): npm run dev"/>
<node CREATED="1765854707560" MODIFIED="1765854707560" TEXT="- t2(web-app): npm run electron:dev"/>
<node CREATED="1765854707561" MODIFIED="1765854707561" TEXT="- Automatically opens the app."/>
</node>
<node CREATED="1765854707565" ID="ID_1618043900" MODIFIED="1765868826830" TEXT="# Deployment">
<node CREATED="1765868836640" FOLDED="true" ID="ID_678208718" MODIFIED="1765868914280" TEXT="Prerequisites">
<node CREATED="1765854707568" ID="ID_1196214065" MODIFIED="1765868852826" TEXT="The icon files (ico and png) should be in ./public folder."/>
</node>
<node CREATED="1765868871261" ID="ID_1087159129" MODIFIED="1765868873186" TEXT="Build">
<node CREATED="1765868894168" ID="ID_1431882531" MODIFIED="1765868896592" TEXT="t1 (web-app)">
<node CREATED="1765854707573" ID="ID_733298924" MODIFIED="1765868901376" TEXT="Remove-Item -Recurse -Force &quot;release&quot;"/>
<node CREATED="1765854707578" ID="ID_1108639207" MODIFIED="1765868893674" TEXT="npm run electron:build:win"/>
</node>
</node>
<node CREATED="1765868859734" FOLDED="true" ID="ID_1117751140" MODIFIED="1765868916130" TEXT="Output">
<node CREATED="1765854707579" ID="ID_1733958911" MODIFIED="1765868866713" TEXT="The setup file will be created in the &quot;release&quot; folder."/>
</node>
</node>
</node>
<node CREATED="1765854717411" FOLDED="true" ID="ID_929084473" MODIFIED="1765859196067" TEXT="Android App">
<node CREATED="1765854717413" FOLDED="true" ID="ID_1811226763" MODIFIED="1765859194137" TEXT="# Setup">
<node CREATED="1765854717413" ID="ID_209187528" MODIFIED="1765854778603" TEXT="npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/filesystem">
<font ITALIC="true" NAME="Calibri" SIZE="20"/>
</node>
<node CREATED="1765854717418" ID="ID_110360202" MODIFIED="1765854778592" TEXT="npx cap init EzeeGenie com.ezeegenie.app --web-dir dist">
<font ITALIC="true" NAME="Calibri" SIZE="20"/>
</node>
<node CREATED="1765854717438" ID="ID_1181230046" MODIFIED="1765854778586" TEXT="npm run build">
<font ITALIC="true" NAME="Calibri" SIZE="20"/>
</node>
<node CREATED="1765854717444" ID="ID_808602436" MODIFIED="1765854778559" TEXT="npx cap add android">
<font ITALIC="true" NAME="Calibri" SIZE="20"/>
</node>
<node CREATED="1765854717444" ID="ID_193769343" LINK="https://developer.android.com/studio" MODIFIED="1765856234694" TEXT="Install Android Studio"/>
</node>
<node CREATED="1765854707556" FOLDED="true" ID="ID_732212354" MODIFIED="1765859190559" TEXT="# Development">
<node CREATED="1765859168709" FOLDED="true" ID="ID_1429834150" MODIFIED="1765859189592" TEXT="Setting up Data (Crucial Step)">
<node CREATED="1765859151835" ID="ID_1920746119" MODIFIED="1765859151835" TEXT="On your Android device, go to Documents."/>
<node CREATED="1765859151856" ID="ID_110144791" MODIFIED="1765859151856" TEXT="Create a folder named EzeeGenie."/>
<node CREATED="1765859151873" ID="ID_946415143" MODIFIED="1765859151873" TEXT="Inside EzeeGenie, copy your entire db folder."/>
<node CREATED="1765859151875" ID="ID_828932251" MODIFIED="1765859151875" TEXT="Path should look like: Internal Storage &gt; Documents &gt; EzeeGenie &gt; db &gt; subject-order.json"/>
<node CREATED="1765859151895" ID="ID_530819041" MODIFIED="1765859185681" TEXT="Internal Storage &gt; Documents &gt; EzeeGenie &gt; db &gt; 6-science &gt; ..."/>
</node>
</node>
<node CREATED="1765854717449" FOLDED="true" ID="ID_854118502" MODIFIED="1765859195213" TEXT="# Deployment">
<node CREATED="1765854717451" ID="ID_1922446289" MODIFIED="1765854816442" TEXT="Building the App:t1(web-app): npm run build:mobile"/>
<node CREATED="1765854717453" ID="ID_820269883" MODIFIED="1765854818043" TEXT="Running on Android: t1(web-app): npx cap open android"/>
<node CREATED="1765854717454" ID="ID_1440316673" MODIFIED="1765854829266" TEXT="From Android Studio, you can run the app on an emulator or a connected device."/>
</node>
</node>
<node CREATED="1765854847968" FOLDED="true" ID="ID_851398907" MODIFIED="1765858018168" TEXT="Existing Word Document Migration">
<node CREATED="1765857951874" MODIFIED="1765857951874" TEXT="1. Convert Chapter level word document to json."/>
<node CREATED="1765857951876" MODIFIED="1765857951876" TEXT="2. Updates db/`&lt;standard&gt;`/`&lt;subject&gt;`.json file."/>
<node CREATED="1765857951892" MODIFIED="1765857951892" TEXT="3. Uploads the images to content-images repository."/>
<node CREATED="1765857951897" MODIFIED="1765857951897" TEXT="4. Pushes the files to content-images repository."/>
<node CREATED="1765857951900" MODIFIED="1765857951900" TEXT="5. The input-file should be in the same folder as the script."/>
<node CREATED="1765857951903" MODIFIED="1765857951903" TEXT="6. The input file name should be in the format `&lt;chapter&gt;`.docx"/>
<node CREATED="1765857951903" MODIFIED="1765857951903" TEXT="7. Do not include topic numbers in the input file name."/>
<node CREATED="1765857959826" MODIFIED="1765857959826" TEXT="Command Line Usage:"/>
<node CREATED="1765857959830" MODIFIED="1765857959830" TEXT="python migration.py `&lt;standard&gt;` `&lt;subject&gt;` `&lt;input-file&gt;`"/>
<node CREATED="1765857959830" MODIFIED="1765857959830" TEXT="Example:"/>
<node CREATED="1765857959834" MODIFIED="1765857959834" TEXT="cd doc-to-json-converter"/>
<node CREATED="1765857959836" MODIFIED="1765857959836" TEXT="python migration.py 6 science 10.docx"/>
</node>
</node>
<node CREATED="1765857839163" FOLDED="true" ID="ID_1703693081" MODIFIED="1765868821749" POSITION="right" TEXT="Requirements">
<node CREATED="1765857851541" ID="ID_1058448795" MODIFIED="1765857859607" TEXT="Q-Gen">
<node CREATED="1765857860676" ID="ID_1231813989" MODIFIED="1765857865303" TEXT="Question paper generator"/>
</node>
<node CREATED="1765857865740" ID="ID_501185965" MODIFIED="1765857925047" TEXT="Material theme conversion"/>
</node>
</node>
</map>
