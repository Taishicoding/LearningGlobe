"""Build the static daily country collection from reviewed, concise fact seeds."""

import json
from pathlib import Path
from urllib.parse import quote


# One country per row: name, ISO code, region, capital, capital lat/lon,
# map-oriented location clue, memorable geography fact, source article slug.
SEEDS = [
    # Africa
    ("Algeria", "DZA", "Africa", "Algiers", 36.75, 3.06, "In North Africa, with the Mediterranean coast to the north and the Sahara across most of its interior.", "The Sahara covers most of Algeria, making it Africa's largest country by area.", "Algeria"),
    ("Angola", "AGO", "Africa", "Luanda", -8.84, 13.23, "On Africa's southwest coast, south of the Republic of the Congo and north of Namibia.", "Angola includes the Cabinda exclave, separated from the rest of the country by a strip of the Democratic Republic of the Congo.", "Angola"),
    ("Benin", "BEN", "Africa", "Porto-Novo", 6.50, 2.63, "A narrow country on the Gulf of Guinea, between Togo and Nigeria.", "Benin stretches from a short Atlantic coast northward into the Sahel, so its landscapes change markedly from south to north.", "Benin"),
    ("Botswana", "BWA", "Africa", "Gaborone", -24.65, 25.91, "A landlocked country in southern Africa, north of South Africa and west of Zimbabwe.", "The Okavango Delta spreads inland across the Kalahari rather than flowing out to the sea.", "Botswana"),
    ("Burkina Faso", "BFA", "Africa", "Ouagadougou", 12.37, -1.53, "A landlocked country in West Africa, south of Mali and north of Ghana and Togo.", "Burkina Faso is one of the few countries whose name is commonly translated as 'Land of Upright People.'", "Burkina_Faso"),
    ("Burundi", "BDI", "Africa", "Gitega", -3.43, 29.93, "A small, landlocked country in the Great Lakes region, south of Rwanda and east of Lake Tanganyika.", "Burundi sits beside Lake Tanganyika, one of the world's deepest freshwater lakes.", "Burundi"),
    ("Cabo Verde", "CPV", "Africa", "Praia", 14.92, -23.51, "An Atlantic island country west of Senegal, off the coast of West Africa.", "Cabo Verde is an archipelago of ten main volcanic islands.", "Cape_Verde"),
    ("Cameroon", "CMR", "Africa", "Yaounde", 3.87, 11.52, "On the Gulf of Guinea, between Nigeria and Central African Republic.", "Mount Cameroon is an active volcano and one of the highest peaks in sub-Saharan West Africa.", "Cameroon"),
    ("Central African Republic", "CAF", "Africa", "Bangui", 4.36, 18.56, "A landlocked country near the centre of Africa, north of the Democratic Republic of the Congo.", "The country lies in the Congo Basin and includes both dense rainforest in the south and savanna in the north.", "Central_African_Republic"),
    ("Chad", "TCD", "Africa", "N'Djamena", 12.11, 15.04, "A large landlocked country linking North and Central Africa, with Libya to its north.", "Lake Chad, which gives the country its name, sits near the meeting point of Chad, Cameroon, Nigeria and Niger.", "Chad"),
    ("Comoros", "COM", "Africa", "Moroni", -11.70, 43.26, "An island country in the Mozambique Channel, between Madagascar and mainland Africa.", "The Comoros are volcanic islands, and Mount Karthala on Grande Comore is an active volcano.", "Comoros"),
    ("Republic of the Congo", "COG", "Africa", "Brazzaville", -4.27, 15.28, "On the Atlantic coast of Central Africa, west of the Democratic Republic of the Congo.", "Brazzaville and Kinshasa, the capitals of the two Congos, face each other across the Congo River.", "Republic_of_the_Congo"),
    ("Cote d'Ivoire", "CIV", "Africa", "Yamoussoukro", 6.82, -5.28, "On the Gulf of Guinea in West Africa, between Liberia and Ghana.", "Yamoussoukro is the political capital, while Abidjan remains the country's largest city and main port.", "Ivory_Coast"),
    ("Democratic Republic of the Congo", "COD", "Africa", "Kinshasa", -4.32, 15.31, "A vast Central African country crossed by the equator and bordered by the Atlantic through a short coastline.", "The Congo River is the world's deepest river and forms part of the country's western boundary.", "Democratic_Republic_of_the_Congo"),
    ("Djibouti", "DJI", "Africa", "Djibouti", 11.59, 43.15, "At the Horn of Africa, beside the Red Sea and the Gulf of Aden.", "Lake Assal in Djibouti is one of the lowest points on land in Africa.", "Djibouti"),
    ("Egypt", "EGY", "Africa", "Cairo", 30.04, 31.24, "In northeast Africa, linking the Mediterranean Sea with the Red Sea and the Sinai Peninsula with Asia.", "Almost all of Egypt's population lives close to the Nile, which crosses the desert and forms a broad delta at the Mediterranean.", "Egypt"),
    ("Equatorial Guinea", "GNQ", "Africa", "Ciudad de la Paz", 1.62, 10.83, "On Central Africa's Atlantic coast; its territory includes the island of Bioko and the mainland region of Rio Muni.", "Equatorial Guinea's capital moved from the island of Bioko to Ciudad de la Paz on the mainland in January 2026.", "Equatorial_Guinea"),
    ("Eritrea", "ERI", "Africa", "Asmara", 15.34, 38.93, "On the Red Sea coast of the Horn of Africa, north of Ethiopia.", "Eritrea's Dahlak Archipelago contains more than a hundred islands in the Red Sea.", "Eritrea"),
    ("Eswatini", "SWZ", "Africa", "Mbabane", -26.32, 31.14, "A small, landlocked country in southern Africa, between South Africa and Mozambique.", "Eswatini is one of Africa's few remaining absolute monarchies.", "Eswatini"),
    ("Ethiopia", "ETH", "Africa", "Addis Ababa", 9.03, 38.74, "A highland country in the Horn of Africa, west of Somalia and south of Eritrea.", "The Blue Nile begins at Lake Tana in Ethiopia before flowing into Sudan.", "Ethiopia"),
    ("Gabon", "GAB", "Africa", "Libreville", 0.39, 9.45, "On the Atlantic coast of Central Africa, straddling the equator.", "Gabon protects a large share of its land in national parks, including forests that form part of the Congo Basin.", "Gabon"),
    ("The Gambia", "GMB", "Africa", "Banjul", 13.45, -16.58, "A narrow West African country that follows the Gambia River inland and is almost surrounded by Senegal.", "The Gambia is mainland Africa's smallest country by area.", "The_Gambia"),
    ("Ghana", "GHA", "Africa", "Accra", 5.56, -0.20, "On the Gulf of Guinea in West Africa, west of Togo and east of Cote d'Ivoire.", "Lake Volta, created by the Akosombo Dam, is one of the world's largest artificial lakes by surface area.", "Ghana"),
    ("Guinea", "GIN", "Africa", "Conakry", 9.54, -13.68, "On West Africa's Atlantic coast, south of Senegal and Guinea-Bissau.", "The Fouta Djallon highlands in Guinea are a source region for several major West African rivers.", "Guinea"),
    ("Guinea-Bissau", "GNB", "Africa", "Bissau", 11.86, -15.60, "On the Atlantic coast of West Africa, between Senegal and Guinea.", "The Bijagos Archipelago off Guinea-Bissau has dozens of islands and is an important nesting area for sea turtles.", "Guinea-Bissau"),
    ("Kenya", "KEN", "Africa", "Nairobi", -1.29, 36.82, "On the Indian Ocean in East Africa, crossed by the equator and the Great Rift Valley.", "Mount Kenya is the second-highest mountain in Africa, after Kilimanjaro.", "Kenya"),
    ("Lesotho", "LSO", "Africa", "Maseru", -29.31, 27.48, "A mountainous, landlocked country entirely surrounded by South Africa.", "Lesotho is the only independent country whose entire territory lies above 1,000 metres in elevation.", "Lesotho"),
    ("Liberia", "LBR", "Africa", "Monrovia", 6.30, -10.80, "On the Atlantic coast of West Africa, between Sierra Leone and Cote d'Ivoire.", "Liberia's coastline includes a chain of lagoons, mangroves and sandy beaches.", "Liberia"),
    ("Libya", "LBY", "Africa", "Tripoli", 32.89, 13.19, "On the Mediterranean coast of North Africa, between Egypt and Tunisia.", "The Sahara covers most of Libya, and the country has one of Africa's longest Mediterranean coastlines.", "Libya"),
    ("Madagascar", "MDG", "Africa", "Antananarivo", -18.91, 47.52, "A large island in the Indian Ocean, off the southeast coast of Africa.", "Madagascar split from other landmasses long ago, leaving many plants and animals found nowhere else.", "Madagascar"),
    ("Malawi", "MWI", "Africa", "Lilongwe", -13.97, 33.79, "A long, landlocked country in southeast Africa, running along Lake Malawi.", "Lake Malawi contains more species of freshwater fish than any other lake, including hundreds of cichlid species.", "Malawi"),
    ("Mali", "MLI", "Africa", "Bamako", 12.64, -8.00, "A large landlocked country in West Africa, stretching from the Sahara south toward the Sahel.", "Timbuktu in Mali was a major centre of trans-Saharan trade and Islamic scholarship.", "Mali"),
    ("Mauritania", "MRT", "Africa", "Nouakchott", 18.09, -15.98, "On the Atlantic edge of northwest Africa, between Western Sahara and Senegal.", "The Richat Structure, a huge circular feature visible from space, lies in Mauritania's Sahara.", "Mauritania"),
    ("Mauritius", "MUS", "Africa", "Port Louis", -20.16, 57.50, "An island country in the Indian Ocean east of Madagascar.", "Mauritius was the only known home of the dodo, a flightless bird that became extinct in the 17th century.", "Mauritius"),
    ("Morocco", "MAR", "Africa", "Rabat", 34.02, -6.84, "At the northwest corner of Africa, with Atlantic and Mediterranean coastlines near the Strait of Gibraltar.", "The Atlas Mountains cross Morocco and include Toubkal, the highest peak in North Africa.", "Morocco"),
    ("Mozambique", "MOZ", "Africa", "Maputo", -25.97, 32.58, "On the Indian Ocean in southeast Africa, with Tanzania to the north and South Africa to the south.", "Mozambique has an Indian Ocean coastline more than 2,400 kilometres long.", "Mozambique"),
    ("Namibia", "NAM", "Africa", "Windhoek", -22.57, 17.08, "On the southwest coast of Africa, between Angola and South Africa.", "Namibia's Namib Desert is often described as one of the world's oldest deserts.", "Namibia"),
    ("Niger", "NER", "Africa", "Niamey", 13.51, 2.12, "A landlocked country in the Sahel, named for the Niger River that crosses its southwest.", "The Sahara occupies much of Niger, while the Niger River valley supports settlement in the south.", "Niger"),
    ("Nigeria", "NGA", "Africa", "Abuja", 9.06, 7.49, "On the Gulf of Guinea in West Africa, between Benin and Cameroon.", "The Niger and Benue rivers meet in Nigeria before flowing south toward the Niger Delta.", "Nigeria"),
    ("Rwanda", "RWA", "Africa", "Kigali", -1.95, 30.06, "A small, landlocked highland country in East Africa, just south of Uganda.", "Rwanda is known as the 'land of a thousand hills' because much of the country is hilly and mountainous.", "Rwanda"),
    ("Sao Tome and Principe", "STP", "Africa", "Sao Tome", 0.34, 6.73, "Two main volcanic islands in the Gulf of Guinea, west of Gabon.", "The equator passes close to Ilheu das Rolas, a small island south of Sao Tome.", "Sao_Tome_and_Principe"),
    ("Senegal", "SEN", "Africa", "Dakar", 14.72, -17.47, "At the westernmost tip of mainland Africa, with the Atlantic Ocean to its west.", "The Cape Verde Peninsula, where Dakar sits, is the westernmost point of mainland Africa.", "Senegal"),
    ("Seychelles", "SYC", "Africa", "Victoria", -4.62, 55.45, "An archipelago in the western Indian Ocean, northeast of Madagascar.", "Seychelles includes both granitic islands and low coral atolls, a rare mix in the Indian Ocean.", "Seychelles"),
    ("Sierra Leone", "SLE", "Africa", "Freetown", 8.48, -13.23, "On the Atlantic coast of West Africa, between Guinea and Liberia.", "Freetown Harbour is one of the largest natural harbours on Africa's west coast.", "Sierra_Leone"),
    ("Somalia", "SOM", "Africa", "Mogadishu", 2.05, 45.32, "At the Horn of Africa, with long coastlines on both the Gulf of Aden and Indian Ocean.", "Somalia has the longest coastline of any mainland African country.", "Somalia"),
    ("South Africa", "ZAF", "Africa", "Pretoria", -25.75, 28.19, "At the southern tip of Africa, with Atlantic and Indian Ocean coasts.", "South Africa has three capital cities: Pretoria, Cape Town and Bloemfontein serve different branches of government.", "South_Africa"),
    ("South Sudan", "SSD", "Africa", "Juba", 4.85, 31.60, "A landlocked country in East-Central Africa, south of Sudan and crossed by the White Nile.", "The Sudd in South Sudan is one of the world's largest tropical wetlands.", "South_Sudan"),
    ("Sudan", "SDN", "Africa", "Khartoum", 15.50, 32.56, "In northeast Africa, where the White and Blue Nile rivers meet at Khartoum.", "More pyramids have been found in Sudan than in Egypt, many built by the ancient Kingdom of Kush.", "Sudan"),
    ("Tanzania", "TZA", "Africa", "Dodoma", -6.16, 35.75, "On East Africa's Indian Ocean coast, including Zanzibar and the slopes of Kilimanjaro.", "Mount Kilimanjaro, Africa's highest mountain, rises in northeastern Tanzania.", "Tanzania"),
    ("Togo", "TGO", "Africa", "Lome", 6.13, 1.22, "A narrow country on the Gulf of Guinea, between Ghana and Benin.", "Togo is only about 50 kilometres wide at its narrowest point, yet stretches far inland from the coast.", "Togo"),
    ("Tunisia", "TUN", "Africa", "Tunis", 36.81, 10.18, "At the northern tip of Africa, between Algeria and Libya, facing the Mediterranean.", "Tunisia contains the eastern end of the Atlas Mountains and the northern edge of the Sahara.", "Tunisia"),
    ("Uganda", "UGA", "Africa", "Kampala", 0.31, 32.58, "A landlocked East African country on the equator, north of Lake Victoria.", "The Nile flows out of Lake Victoria in Uganda on its long journey north toward the Mediterranean.", "Uganda"),
    ("Zambia", "ZMB", "Africa", "Lusaka", -15.42, 28.28, "A landlocked country in southern Africa, north of Zimbabwe and Botswana.", "Victoria Falls lies on the Zambia-Zimbabwe border, where the Zambezi River plunges into a narrow gorge.", "Zambia"),
    ("Zimbabwe", "ZWE", "Africa", "Harare", -17.83, 31.05, "A landlocked southern African country between Zambia, Mozambique, Botswana and South Africa.", "The name Zimbabwe comes from Great Zimbabwe, the remains of a major medieval stone city.", "Zimbabwe"),
    # Asia
    ("Afghanistan", "AFG", "Asia", "Kabul", 34.52, 69.18, "A landlocked country at the crossroads of Central and South Asia.", "The Hindu Kush mountain range runs through Afghanistan and separates many northern and southern valleys.", "Afghanistan"),
    ("Armenia", "ARM", "Asia", "Yerevan", 40.18, 44.51, "A landlocked country in the South Caucasus, between Turkey and Azerbaijan.", "Mount Ararat is visible from much of Armenia, although it lies across the border in Turkey.", "Armenia"),
    ("Azerbaijan", "AZE", "Asia", "Baku", 40.41, 49.87, "On the western shore of the Caspian Sea, at the meeting of eastern Europe and western Asia.", "Baku sits below sea level on the Caspian coast, making it one of the world's lowest-lying national capitals.", "Azerbaijan"),
    ("Bahrain", "BHR", "Asia", "Manama", 26.23, 50.58, "A small island country in the Persian Gulf, east of Saudi Arabia.", "Bahrain's name means 'two seas' in Arabic, and the country is an archipelago of more than 30 islands.", "Bahrain"),
    ("Bangladesh", "BGD", "Asia", "Dhaka", 23.81, 90.41, "At the northern edge of the Bay of Bengal, mostly within the Ganges-Brahmaputra delta.", "Bangladesh is shaped by the world's largest river delta, formed by the Ganges, Brahmaputra and Meghna rivers.", "Bangladesh"),
    ("Bhutan", "BTN", "Asia", "Thimphu", 27.47, 89.64, "A small Himalayan country between India and China.", "Bhutan's landscape rises from subtropical plains to the high Himalaya in a relatively short distance.", "Bhutan"),
    ("Brunei", "BRN", "Asia", "Bandar Seri Begawan", 4.94, 114.95, "On the north coast of Borneo, surrounded by the Malaysian state of Sarawak except along its coast.", "Brunei is split into two parts by a strip of Malaysian territory.", "Brunei"),
    ("Cambodia", "KHM", "Asia", "Phnom Penh", 11.56, 104.92, "In mainland Southeast Asia, between Thailand, Laos and Vietnam.", "Tonle Sap Lake in Cambodia expands dramatically during the monsoon as the Tonle Sap River reverses direction.", "Cambodia"),
    ("China", "CHN", "Asia", "Beijing", 39.90, 116.40, "In East Asia, with a long Pacific coastline and borders across Central, South and East Asia.", "The Yangtze is the longest river in Asia and flows entirely within China.", "China"),
    ("Cyprus", "CYP", "Asia", "Nicosia", 35.17, 33.36, "An island in the eastern Mediterranean, south of Turkey and west of Syria.", "Cyprus is the third-largest island in the Mediterranean Sea, after Sicily and Sardinia.", "Cyprus"),
    ("Georgia", "GEO", "Asia", "Tbilisi", 41.72, 44.79, "On the Black Sea at the southern edge of the Caucasus Mountains.", "The Greater Caucasus forms much of Georgia's northern boundary and contains some of Europe's highest peaks.", "Georgia_(country)"),
    ("India", "IND", "Asia", "New Delhi", 28.61, 77.21, "A large South Asian peninsula between the Arabian Sea and Bay of Bengal, with the Himalaya to the north.", "The Himalaya in northern India include Kanchenjunga, the world's third-highest mountain.", "India"),
    ("Indonesia", "IDN", "Asia", "Jakarta", -6.21, 106.85, "An archipelago straddling the equator between the Indian and Pacific oceans.", "Indonesia has more active volcanoes than any other country because it lies along the Pacific Ring of Fire.", "Indonesia"),
    ("Iran", "IRN", "Asia", "Tehran", 35.69, 51.39, "A large country in western Asia, between the Caspian Sea and the Persian Gulf.", "The Zagros and Alborz mountain ranges enclose Iran's central plateau.", "Iran"),
    ("Iraq", "IRQ", "Asia", "Baghdad", 33.31, 44.37, "In western Asia, between Turkey, Iran, the Persian Gulf and the deserts of Arabia.", "The Tigris and Euphrates rivers meet in southern Iraq before flowing toward the Persian Gulf.", "Iraq"),
    ("Israel", "ISR", "Asia", "Jerusalem (Israel's declared capital; status is disputed internationally)", 31.77, 35.21, "On the eastern Mediterranean, at the southwest edge of Asia.", "The Dead Sea, shared by Israel, Jordan and the West Bank, is Earth's lowest land elevation.", "Israel"),
    ("Japan", "JPN", "Asia", "Tokyo", 35.68, 139.69, "An island arc in the northwest Pacific, east of the Korean Peninsula and China.", "Japan consists of thousands of islands, with most people living on its four largest: Honshu, Hokkaido, Kyushu and Shikoku.", "Japan"),
    ("Jordan", "JOR", "Asia", "Amman", 31.95, 35.93, "A mostly landlocked Middle Eastern country with a short coastline on the Gulf of Aqaba.", "Jordan's Dead Sea coast includes the lowest exposed land on Earth.", "Jordan"),
    ("Kazakhstan", "KAZ", "Asia", "Astana", 51.17, 71.43, "A vast Central Asian country extending from the Caspian Sea toward the Altai Mountains.", "Kazakhstan is the world's largest landlocked country.", "Kazakhstan"),
    ("Kuwait", "KWT", "Asia", "Kuwait City", 29.38, 47.99, "At the northwestern end of the Persian Gulf, between Iraq and Saudi Arabia.", "Kuwait includes several islands in the Persian Gulf, including Bubiyan, its largest island.", "Kuwait"),
    ("Kyrgyzstan", "KGZ", "Asia", "Bishkek", 42.87, 74.59, "A mountainous, landlocked country in Central Asia, west of China.", "The Tian Shan mountains cover most of Kyrgyzstan, and Lake Issyk-Kul is one of the world's largest high-altitude lakes.", "Kyrgyzstan"),
    ("Laos", "LAO", "Asia", "Vientiane", 17.97, 102.63, "A landlocked country in mainland Southeast Asia, between Thailand and Vietnam; the Mekong forms much of its western border.", "Laos is the only landlocked country in Southeast Asia.", "Laos"),
    ("Lebanon", "LBN", "Asia", "Beirut", 33.89, 35.50, "A small country on the eastern Mediterranean, with the Anti-Lebanon range on its eastern edge.", "The Lebanon Mountains run parallel to the Mediterranean coast, creating a narrow coastal plain and a high interior.", "Lebanon"),
    ("Malaysia", "MYS", "Asia", "Kuala Lumpur", 3.14, 101.69, "Two regions straddle the South China Sea: the Malay Peninsula and northern Borneo.", "Malaysia is one of the few countries with territory on both the Asian mainland and the island of Borneo.", "Malaysia"),
    ("Maldives", "MDV", "Asia", "Male", 4.18, 73.51, "A chain of coral atolls in the Indian Ocean southwest of India and Sri Lanka.", "The Maldives is the world's lowest-lying country, with a very low average elevation.", "Maldives"),
    ("Mongolia", "MNG", "Asia", "Ulaanbaatar", 47.92, 106.92, "A landlocked country between Russia and China, dominated by high plains and steppe.", "The Gobi Desert spans southern Mongolia and northern China.", "Mongolia"),
    ("Myanmar", "MMR", "Asia", "Naypyidaw", 19.76, 96.08, "In mainland Southeast Asia, with a long coastline on the Bay of Bengal and Andaman Sea.", "The Irrawaddy River runs through Myanmar from the Himalaya foothills to a broad delta on the Andaman Sea.", "Myanmar"),
    ("Nepal", "NPL", "Asia", "Kathmandu", 27.72, 85.32, "A narrow, landlocked Himalayan country between India and China.", "Eight of the world's ten highest mountains, including Mount Everest, lie on or near Nepal's borders.", "Nepal"),
    ("North Korea", "PRK", "Asia", "Pyongyang", 39.04, 125.76, "On the northern half of the Korean Peninsula, between China, Russia and South Korea.", "The Demilitarized Zone separates North and South Korea across the peninsula.", "North_Korea"),
    ("Oman", "OMN", "Asia", "Muscat", 23.59, 58.41, "On the southeastern edge of the Arabian Peninsula, facing both the Arabian Sea and Gulf of Oman.", "Oman's Musandam Peninsula is separated from the rest of the country by the United Arab Emirates and overlooks the Strait of Hormuz.", "Oman"),
    ("Pakistan", "PAK", "Asia", "Islamabad", 33.69, 73.06, "In South Asia, from the Arabian Sea northward to the high Karakoram and Himalaya.", "K2, the world's second-highest mountain, stands in Pakistan's Karakoram range.", "Pakistan"),
    ("Palestine", "PSE", "Asia", "East Jerusalem (claimed capital); Ramallah is the administrative centre", 31.90, 35.20, "The Palestinian territories comprise the West Bank, east of Israel, and Gaza on the Mediterranean coast.", "The West Bank includes the Jordan Valley and the Dead Sea's northwestern shore.", "State_of_Palestine"),
    ("Philippines", "PHL", "Asia", "Manila", 14.60, 120.98, "An archipelago in the western Pacific, south of Taiwan and north of Indonesia.", "The Philippines is made up of more than 7,000 islands, grouped around Luzon, Visayas and Mindanao.", "Philippines"),
    ("Qatar", "QAT", "Asia", "Doha", 25.29, 51.53, "A small peninsula extending into the Persian Gulf from Saudi Arabia.", "Qatar is a peninsula whose only land border is with Saudi Arabia.", "Qatar"),
    ("Saudi Arabia", "SAU", "Asia", "Riyadh", 24.71, 46.67, "Occupies most of the Arabian Peninsula, between the Red Sea and Persian Gulf.", "The Rub' al Khali, or Empty Quarter, is the world's largest continuous sand desert and covers part of southern Saudi Arabia.", "Saudi_Arabia"),
    ("Singapore", "SGP", "Asia", "Singapore", 1.29, 103.85, "A small island city-state at the southern tip of the Malay Peninsula.", "Singapore sits beside the Strait of Malacca, one of the world's busiest shipping routes.", "Singapore"),
    ("South Korea", "KOR", "Asia", "Seoul", 37.57, 126.98, "On the southern half of the Korean Peninsula, facing Japan across the Korea Strait.", "South Korea's Jeju Island is a volcanic island formed around Hallasan, the country's highest mountain.", "South_Korea"),
    ("Sri Lanka", "LKA", "Asia", "Sri Jayawardenepura Kotte (legislative capital; Colombo is the largest city)", 6.89, 79.90, "An island in the Indian Ocean just southeast of India.", "Sri Lanka is known as the 'island of gems' and has a mountainous central highland surrounded by coastal plains.", "Sri_Lanka"),
    ("Syria", "SYR", "Asia", "Damascus", 33.51, 36.29, "In western Asia, between the Mediterranean coast and the Euphrates valley.", "The Euphrates, one of the great rivers of ancient Mesopotamia, crosses eastern Syria.", "Syria"),
    ("Tajikistan", "TJK", "Asia", "Dushanbe", 38.56, 68.78, "A mountainous, landlocked country in Central Asia, bordering Afghanistan to the south.", "More than 90 percent of Tajikistan is mountainous, with the Pamirs rising in its east.", "Tajikistan"),
    ("Thailand", "THA", "Asia", "Bangkok", 13.76, 100.50, "In mainland Southeast Asia, with a long peninsula reaching toward Malaysia.", "Thailand is the only Southeast Asian country never formally colonised by a European power.", "Thailand"),
    ("Timor-Leste", "TLS", "Asia", "Dili", -8.56, 125.57, "On the eastern half of Timor island, north of Australia in the Lesser Sunda Islands.", "Timor-Leste is one of Asia's newest countries and occupies the eastern end of Timor island.", "Timor-Leste"),
    ("Turkey", "TUR", "Asia", "Ankara", 39.93, 32.86, "Spans western Asia and southeastern Europe, with the Bosporus separating the two parts.", "The Bosporus, a narrow strait through Istanbul, links the Black Sea with the Sea of Marmara.", "Turkey"),
    ("Turkmenistan", "TKM", "Asia", "Ashgabat", 37.95, 58.38, "A mostly desert, landlocked country in Central Asia, bordering the Caspian Sea.", "The Karakum Desert covers much of Turkmenistan, and the Karakum Canal crosses it for hundreds of kilometres.", "Turkmenistan"),
    ("United Arab Emirates", "ARE", "Asia", "Abu Dhabi", 24.45, 54.65, "On the southeastern coast of the Persian Gulf, between Qatar and Oman.", "The UAE is a federation of seven emirates, including Abu Dhabi and Dubai.", "United_Arab_Emirates"),
    ("Uzbekistan", "UZB", "Asia", "Tashkent", 41.30, 69.28, "A landlocked country in Central Asia, between the Caspian region and the Tian Shan.", "Uzbekistan is one of only two doubly landlocked countries in the world; every neighbouring country is also landlocked.", "Uzbekistan"),
    ("Vietnam", "VNM", "Asia", "Hanoi", 21.03, 105.85, "A long, narrow country on the South China Sea in mainland Southeast Asia.", "Vietnam's coastline curves in an S shape for more than 3,000 kilometres.", "Vietnam"),
    ("Yemen", "YEM", "Asia", "Sanaa", 15.35, 44.21, "At the southern end of the Arabian Peninsula, facing the Red Sea and Gulf of Aden.", "The Socotra Archipelago off Yemen is known for plant life found nowhere else, including the dragon's blood tree.", "Yemen"),
    # Europe
    ("Albania", "ALB", "Europe", "Tirana", 41.33, 19.82, "On the Adriatic and Ionian seas in southeastern Europe, north of Greece.", "Albania's coastline meets both the Adriatic Sea and the Ionian Sea.", "Albania"),
    ("Andorra", "AND", "Europe", "Andorra la Vella", 42.51, 1.52, "A tiny, landlocked country high in the Pyrenees between France and Spain.", "Andorra la Vella is Europe's highest capital city by elevation.", "Andorra"),
    ("Austria", "AUT", "Europe", "Vienna", 48.21, 16.37, "A landlocked Central European country crossed by the eastern Alps and the Danube.", "The Danube flows through Vienna and continues eastward through several European capitals.", "Austria"),
    ("Belarus", "BLR", "Europe", "Minsk", 53.90, 27.57, "A landlocked country in eastern Europe, between Poland and Russia.", "Belovezhskaya Pushcha, shared with Poland, is one of Europe's last and largest primeval forests.", "Belarus"),
    ("Belgium", "BEL", "Europe", "Brussels", 50.85, 4.35, "In western Europe, between France, Germany, the Netherlands and the North Sea.", "Belgium has three official languages: Dutch, French and German, reflecting its position between language regions.", "Belgium"),
    ("Bosnia and Herzegovina", "BIH", "Europe", "Sarajevo", 43.86, 18.41, "In the western Balkans, with a short Adriatic coastline and mountains inland.", "Bosnia and Herzegovina's only seaside outlet is a short stretch of coast around Neum.", "Bosnia_and_Herzegovina"),
    ("Bulgaria", "BGR", "Europe", "Sofia", 42.70, 23.32, "In southeastern Europe, between the Danube River and the Black Sea.", "The Balkan Mountains run across Bulgaria and give the Balkan Peninsula its name.", "Bulgaria"),
    ("Croatia", "HRV", "Europe", "Zagreb", 45.81, 15.98, "On the Adriatic Sea, with a long indented coast opposite Italy.", "Croatia's Adriatic coastline includes more than a thousand islands and islets.", "Croatia"),
    ("Czechia", "CZE", "Europe", "Prague", 50.08, 14.44, "A landlocked country in Central Europe, between Germany, Poland, Slovakia and Austria.", "The Vltava River flows through Prague before joining the Elbe, which eventually reaches the North Sea.", "Czech_Republic"),
    ("Denmark", "DNK", "Europe", "Copenhagen", 55.68, 12.57, "At the entrance to the Baltic Sea, including the Jutland Peninsula and many islands.", "Denmark's Kingdom includes Greenland and the Faroe Islands, far beyond mainland Europe.", "Denmark"),
    ("Estonia", "EST", "Europe", "Tallinn", 59.44, 24.75, "On the eastern shore of the Baltic Sea, south of Finland across the Gulf of Finland.", "Estonia has more than 2,000 islands, most of them small and uninhabited.", "Estonia"),
    ("Finland", "FIN", "Europe", "Helsinki", 60.17, 24.94, "In northern Europe, between Sweden and Russia, with a long Baltic coastline.", "Finland is often called the 'Land of a Thousand Lakes,' though it has roughly 188,000 lakes.", "Finland"),
    ("France", "FRA", "Europe", "Paris", 48.86, 2.35, "In western Europe, facing the Atlantic and Mediterranean and sharing borders with several neighbours.", "France has coastlines on both the Atlantic Ocean and the Mediterranean Sea.", "France"),
    ("Germany", "DEU", "Europe", "Berlin", 52.52, 13.40, "In central Europe, between the North Sea and Baltic Sea in the north and the Alps in the south.", "The Rhine, Elbe and Danube are three major rivers that begin or flow through Germany.", "Germany"),
    ("Greece", "GRC", "Europe", "Athens", 37.98, 23.73, "At the southern end of the Balkans, extending into the Aegean and Ionian seas.", "Greece has thousands of islands and islets, but only a few hundred are inhabited.", "Greece"),
    ("Holy See", "VAT", "Europe", "Vatican City", 41.90, 12.45, "A tiny independent state enclosed within the city of Rome, Italy.", "The Holy See's territory, Vatican City, is the world's smallest independent state by area.", "Vatican_City"),
    ("Hungary", "HUN", "Europe", "Budapest", 47.50, 19.04, "A landlocked country in Central Europe, centred on the Danube Basin.", "The Danube divides Budapest into Buda and Pest, which were united as one city in 1873.", "Hungary"),
    ("Iceland", "ISL", "Europe", "Reykjavik", 64.15, -21.94, "An island in the North Atlantic, between Greenland and Norway.", "Iceland sits on the Mid-Atlantic Ridge, where the North American and Eurasian plates are moving apart.", "Iceland"),
    ("Ireland", "IRL", "Europe", "Dublin", 53.35, -6.26, "An island in the North Atlantic west of Great Britain.", "The River Shannon is the longest river in Ireland and flows through the island's central lowlands.", "Ireland"),
    ("Italy", "ITA", "Europe", "Rome", 41.90, 12.50, "A boot-shaped peninsula in the Mediterranean, extending south from the Alps.", "Italy includes two independent states entirely surrounded by its territory: San Marino and Vatican City.", "Italy"),
    ("Latvia", "LVA", "Europe", "Riga", 56.95, 24.11, "On the Baltic Sea between Estonia and Lithuania.", "The Daugava River runs through Riga and has long connected the Baltic coast with inland trade routes.", "Latvia"),
    ("Liechtenstein", "LIE", "Europe", "Vaduz", 47.14, 9.52, "A small, landlocked Alpine country between Switzerland and Austria.", "Liechtenstein is one of only two doubly landlocked countries, along with Uzbekistan.", "Liechtenstein"),
    ("Lithuania", "LTU", "Europe", "Vilnius", 54.69, 25.28, "The southernmost Baltic country, on the Baltic Sea between Latvia and Poland.", "The Curonian Spit, shared by Lithuania and Russia, is a narrow sand-dune peninsula along the Baltic coast.", "Lithuania"),
    ("Luxembourg", "LUX", "Europe", "Luxembourg", 49.61, 6.13, "A small, landlocked country between Belgium, France and Germany.", "Luxembourg is one of the world's few remaining grand duchies.", "Luxembourg"),
    ("Malta", "MLT", "Europe", "Valletta", 35.90, 14.51, "A small island country in the central Mediterranean, south of Sicily.", "Malta has been a crossroads between Europe and North Africa because of its position in the central Mediterranean.", "Malta"),
    ("Moldova", "MDA", "Europe", "Chisinau", 47.01, 28.86, "A landlocked country between Romania and Ukraine in eastern Europe.", "Moldova's Milestii Mici wine cellar extends for more than 200 kilometres underground, with a portion used for wine storage.", "Moldova"),
    ("Monaco", "MCO", "Europe", "Monaco", 43.74, 7.42, "A tiny Mediterranean state on the French Riviera, near the Italian border.", "Monaco is the world's second-smallest sovereign state, after Vatican City.", "Monaco"),
    ("Montenegro", "MNE", "Europe", "Podgorica", 42.43, 19.26, "On the Adriatic coast of the western Balkans, south of Croatia.", "The Bay of Kotor is a deep, fjord-like inlet on Montenegro's Adriatic coast.", "Montenegro"),
    ("Netherlands", "NLD", "Europe", "Amsterdam", 52.37, 4.90, "In northwestern Europe, on the North Sea delta of the Rhine, Meuse and Scheldt rivers.", "A large part of the Netherlands lies at or below sea level and is protected by dikes and dunes.", "Netherlands"),
    ("North Macedonia", "MKD", "Europe", "Skopje", 42.00, 21.43, "A landlocked country in the central Balkans, north of Greece.", "Lake Ohrid, shared by North Macedonia and Albania, is one of Europe's oldest and deepest lakes.", "North_Macedonia"),
    ("Norway", "NOR", "Europe", "Oslo", 59.91, 10.75, "On the Scandinavian Peninsula, with a long North Atlantic coastline cut by fjords.", "Norway's coastline is deeply indented by fjords carved by glaciers.", "Norway"),
    ("Poland", "POL", "Europe", "Warsaw", 52.23, 21.01, "In central Europe, with the Baltic Sea to the north and the Carpathians to the south.", "The Vistula is Poland's longest river and flows through Warsaw before reaching the Baltic Sea.", "Poland"),
    ("Portugal", "PRT", "Europe", "Lisbon", 38.72, -9.14, "On the western edge of the Iberian Peninsula, facing the Atlantic Ocean.", "Portugal's Azores and Madeira islands extend far into the Atlantic, southwest of mainland Europe.", "Portugal"),
    ("Romania", "ROU", "Europe", "Bucharest", 44.43, 26.10, "In southeastern Europe, with the Carpathian Mountains and a Danube delta on the Black Sea.", "The Danube Delta in Romania is one of Europe's largest and best-preserved wetlands.", "Romania"),
    ("Russia", "RUS", "Europe", "Moscow", 55.76, 37.62, "Spans eastern Europe and northern Asia, from the Baltic Sea to the Pacific Ocean.", "Russia is the world's largest country by area and spans eleven time zones.", "Russia"),
    ("San Marino", "SMR", "Europe", "San Marino", 43.94, 12.45, "A tiny, landlocked country surrounded by Italy, near the Adriatic coast.", "San Marino is one of the world's oldest republics, traditionally tracing its founding to 301 CE.", "San_Marino"),
    ("Serbia", "SRB", "Europe", "Belgrade", 44.82, 20.46, "A landlocked country in the western Balkans, where the Sava joins the Danube.", "Belgrade stands where the Sava River meets the Danube, a strategic crossroads for centuries.", "Serbia"),
    ("Slovakia", "SVK", "Europe", "Bratislava", 48.15, 17.11, "A landlocked Central European country, with the Carpathian Mountains across its north.", "The Danube flows through Bratislava, making it one of the few capital cities on the river.", "Slovakia"),
    ("Slovenia", "SVN", "Europe", "Ljubljana", 46.06, 14.51, "Where the Alps, Adriatic coast and Balkan Peninsula meet in central Europe.", "Slovenia has a short Adriatic coastline as well as Alpine peaks and karst caves.", "Slovenia"),
    ("Spain", "ESP", "Europe", "Madrid", 40.42, -3.70, "Occupies most of the Iberian Peninsula, facing both the Atlantic and Mediterranean.", "Spain includes the Balearic Islands in the Mediterranean and the Canary Islands off northwest Africa.", "Spain"),
    ("Sweden", "SWE", "Europe", "Stockholm", 59.33, 18.07, "On the eastern side of the Scandinavian Peninsula, between Norway and the Baltic Sea.", "Sweden has thousands of coastal islands, including the large islands of Gotland and Oland in the Baltic.", "Sweden"),
    ("Switzerland", "CHE", "Europe", "Bern", 46.95, 7.45, "A landlocked Alpine country at the meeting point of France, Germany, Italy and Austria.", "The Rhine, Rhone and Inn rivers all rise in the Swiss Alps and flow toward different seas.", "Switzerland"),
    ("Ukraine", "UKR", "Europe", "Kyiv", 50.45, 30.52, "In eastern Europe, with a Black Sea coastline and the Carpathians in its west.", "The Dnipro River crosses Ukraine from north to south and passes through Kyiv.", "Ukraine"),
    ("United Kingdom", "GBR", "Europe", "London", 51.51, -0.13, "An island country northwest of mainland Europe, across the English Channel and North Sea.", "The United Kingdom is made up of Great Britain, Northern Ireland and many smaller islands.", "United_Kingdom"),
    # Americas
    ("Antigua and Barbuda", "ATG", "Americas", "Saint John's", 17.12, -61.85, "A two-island country in the eastern Caribbean, southeast of Puerto Rico.", "Antigua and Barbuda includes many smaller islands, reefs and offshore cays as well as its two main islands.", "Antigua_and_Barbuda"),
    ("Argentina", "ARG", "Americas", "Buenos Aires", -34.60, -58.38, "In southern South America, stretching from the Andes to the South Atlantic.", "Aconcagua in the Andes is the highest mountain outside Asia.", "Argentina"),
    ("The Bahamas", "BHS", "Americas", "Nassau", 25.06, -77.35, "An Atlantic archipelago southeast of Florida and north of Cuba.", "The Bahamas consists of more than 700 islands and cays, many of them uninhabited.", "The_Bahamas"),
    ("Barbados", "BRB", "Americas", "Bridgetown", 13.10, -59.62, "An island in the eastern Caribbean, east of the main arc of the Lesser Antilles.", "Barbados is made largely of coral limestone rather than being a volcanic island like many nearby Caribbean islands.", "Barbados"),
    ("Belize", "BLZ", "Americas", "Belmopan", 17.25, -88.77, "On the Caribbean coast of Central America, south of Mexico and east of Guatemala.", "Belize is home to part of the Belize Barrier Reef, the second-largest barrier reef system in the world.", "Belize"),
    ("Bolivia", "BOL", "Americas", "Sucre (constitutional; La Paz is the seat of government)", -19.03, -65.26, "A landlocked country in central South America, with Andean highlands in the west.", "Bolivia shares Lake Titicaca, the world's highest large navigable lake, with Peru.", "Bolivia"),
    ("Brazil", "BRA", "Americas", "Brasilia", -15.79, -47.88, "The largest country in South America, facing the Atlantic and containing much of the Amazon Basin.", "The Amazon River carries more water than any other river and drains a huge part of Brazil.", "Brazil"),
    ("Canada", "CAN", "Americas", "Ottawa", 45.42, -75.70, "Occupies most of northern North America, with Arctic, Atlantic and Pacific coasts.", "Canada has the world's longest coastline, bordering three oceans.", "Canada"),
    ("Chile", "CHL", "Americas", "Santiago", -33.45, -70.67, "A long, narrow country between the Andes and Pacific Ocean along South America's west coast.", "Chile stretches across more than 38 degrees of latitude, from the Atacama Desert to subantarctic islands.", "Chile"),
    ("Colombia", "COL", "Americas", "Bogota", 4.71, -74.07, "In northwest South America, with coastlines on both the Caribbean Sea and Pacific Ocean.", "Colombia is the only South American country with coastlines on both the Pacific and Atlantic basins.", "Colombia"),
    ("Costa Rica", "CRI", "Americas", "San Jose", 9.93, -84.08, "A narrow Central American country between Nicaragua and Panama, with two ocean coasts.", "Costa Rica protects a large share of its land in national parks and reserves, including tropical rainforests.", "Costa_Rica"),
    ("Cuba", "CUB", "Americas", "Havana", 23.11, -82.37, "The largest Caribbean island, south of Florida and west of Hispaniola.", "Cuba is an archipelago with one main island and more than 4,000 smaller islands and cays.", "Cuba"),
    ("Dominica", "DMA", "Americas", "Roseau", 15.30, -61.39, "A volcanic island in the eastern Caribbean between Guadeloupe and Martinique.", "Dominica is nicknamed the 'Nature Island' for its mountainous rainforests, hot springs and many rivers.", "Dominica"),
    ("Dominican Republic", "DOM", "Americas", "Santo Domingo", 18.49, -69.90, "On the eastern two-thirds of Hispaniola, sharing the island with Haiti.", "The Dominican Republic contains Pico Duarte, the highest mountain in the Caribbean.", "Dominican_Republic"),
    ("Ecuador", "ECU", "Americas", "Quito", -0.18, -78.47, "On South America's Pacific coast, crossed by the equator and including the Galapagos Islands.", "The Galapagos Islands lie about 1,000 kilometres west of mainland Ecuador and are part of the country.", "Ecuador"),
    ("El Salvador", "SLV", "Americas", "San Salvador", 13.69, -89.19, "On the Pacific coast of Central America, between Guatemala and Honduras.", "El Salvador is the smallest and most densely populated country in mainland Central America.", "El_Salvador"),
    ("Grenada", "GRD", "Americas", "Saint George's", 12.05, -61.75, "A small island country in the southeastern Caribbean, north of Trinidad and Tobago.", "Grenada is known as the 'Spice Isle' because nutmeg and other spices grow there.", "Grenada"),
    ("Guatemala", "GTM", "Americas", "Guatemala City", 14.63, -90.51, "In Central America, between Mexico, Belize, Honduras and El Salvador.", "Guatemala has more than 30 volcanoes, several of which are active.", "Guatemala"),
    ("Guyana", "GUY", "Americas", "Georgetown", 6.80, -58.16, "On the Atlantic coast of northern South America, between Venezuela and Suriname.", "Kaieteur Falls in Guyana is one of the world's tallest single-drop waterfalls by volume of water.", "Guyana"),
    ("Haiti", "HTI", "Americas", "Port-au-Prince", 18.54, -72.34, "On the western third of Hispaniola in the Caribbean, sharing the island with the Dominican Republic.", "Haiti's Citadelle Laferriere is a large mountaintop fortress built after independence.", "Haiti"),
    ("Honduras", "HND", "Americas", "Tegucigalpa", 14.08, -87.21, "In Central America, with a Caribbean coast and a small Pacific outlet on the Gulf of Fonseca.", "Honduras is the only Central American country with coastlines on both the Caribbean Sea and Pacific Ocean through the Gulf of Fonseca.", "Honduras"),
    ("Jamaica", "JAM", "Americas", "Kingston", 17.97, -76.79, "An island in the Caribbean Sea south of Cuba and west of Hispaniola.", "The Blue Mountains of Jamaica rise above 2,000 metres despite the island's small area.", "Jamaica"),
    ("Mexico", "MEX", "Americas", "Mexico City", 19.43, -99.13, "At the southern end of North America, between the Pacific and Gulf of Mexico.", "Mexico City was built on the site of Tenochtitlan, an island city in Lake Texcoco.", "Mexico"),
    ("Nicaragua", "NIC", "Americas", "Managua", 12.13, -86.25, "In Central America between Honduras and Costa Rica, with coasts on both oceans.", "Lake Nicaragua is Central America's largest lake and contains freshwater sharks, likely descended from ocean-going species.", "Nicaragua"),
    ("Panama", "PAN", "Americas", "Panama City", 8.98, -79.52, "A narrow isthmus connecting North and South America, between the Caribbean and Pacific.", "The Panama Canal cuts across the isthmus and lets ships pass between the Atlantic and Pacific without sailing around South America.", "Panama"),
    ("Paraguay", "PRY", "Americas", "Asuncion", -25.28, -57.64, "A landlocked country in central South America, divided by the Paraguay River.", "The Paraguay River divides the country into an eastern region and the sparsely populated Gran Chaco to the west.", "Paraguay"),
    ("Peru", "PER", "Americas", "Lima", -12.05, -77.04, "On the Pacific coast of western South America, from the Andes to the Amazon rainforest.", "The Andes run the length of Peru, while the Amazon River's headwaters begin in the country's highlands.", "Peru"),
    ("Saint Kitts and Nevis", "KNA", "Americas", "Basseterre", 17.30, -62.73, "Two volcanic islands in the eastern Caribbean, west of Antigua.", "Saint Kitts and Nevis is the smallest sovereign state in the Western Hemisphere by both area and population.", "Saint_Kitts_and_Nevis"),
    ("Saint Lucia", "LCA", "Americas", "Castries", 14.01, -60.99, "A volcanic island in the eastern Caribbean, south of Martinique.", "The Pitons, two steep volcanic peaks on Saint Lucia's coast, are a UNESCO World Heritage site.", "Saint_Lucia"),
    ("Saint Vincent and the Grenadines", "VCT", "Americas", "Kingstown", 13.16, -61.23, "An island chain in the eastern Caribbean, between Saint Lucia and Grenada.", "The country includes the main island of Saint Vincent and more than 30 smaller Grenadine islands.", "Saint_Vincent_and_the_Grenadines"),
    ("Suriname", "SUR", "Americas", "Paramaribo", 5.85, -55.17, "On the Atlantic coast of northern South America, east of Guyana and west of French Guiana.", "Most of Suriname is covered by tropical rainforest, while most people live near the coast.", "Suriname"),
    ("Trinidad and Tobago", "TTO", "Americas", "Port of Spain", 10.67, -61.52, "Two islands just off Venezuela's northeast coast, at the southern end of the Caribbean.", "Trinidad was once connected to mainland South America, which helps explain its rich wildlife.", "Trinidad_and_Tobago"),
    ("United States", "USA", "Americas", "Washington, D.C.", 38.90, -77.04, "Spans central North America, with Atlantic, Pacific and Arctic coastlines through Alaska.", "The United States includes 50 states spread across a huge range of climates, from Arctic Alaska to tropical Hawaii.", "United_States"),
    ("Uruguay", "URY", "Americas", "Montevideo", -34.90, -56.16, "On South America's Atlantic coast, between Brazil and Argentina at the mouth of the Río de la Plata.", "Uruguay lies entirely in the temperate zone south of the Tropic of Capricorn.", "Uruguay"),
    ("Venezuela", "VEN", "Americas", "Caracas", 10.49, -66.88, "In northern South America, facing the Caribbean Sea and sharing the Orinoco basin.", "Angel Falls in Venezuela is the world's highest uninterrupted waterfall.", "Venezuela"),
    # Oceania
    ("Australia", "AUS", "Oceania", "Canberra", -35.28, 149.13, "Between the Indian and Pacific oceans, south of Indonesia and Papua New Guinea.", "Australia is the only country that governs an entire continent; it also includes Tasmania and many smaller islands.", "Australia"),
    ("Fiji", "FJI", "Oceania", "Suva", -18.14, 178.44, "An island country in the South Pacific, east of Vanuatu and west of Tonga.", "Fiji is an archipelago of more than 300 islands, though only about a third are inhabited.", "Fiji"),
    ("Kiribati", "KIR", "Oceania", "South Tarawa", 1.33, 172.98, "A Pacific island country whose atolls straddle the equator and the International Date Line.", "Kiribati is the only country that lies in all four hemispheres: north, south, east and west.", "Kiribati"),
    ("Marshall Islands", "MHL", "Oceania", "Majuro", 7.09, 171.38, "A chain of atolls in the central Pacific, northeast of Micronesia.", "The Marshall Islands consists of 29 atolls and five individual islands spread across a vast area of ocean.", "Marshall_Islands"),
    ("Federated States of Micronesia", "FSM", "Oceania", "Palikir", 6.92, 158.16, "Four island states spread across the western Pacific, north of Papua New Guinea.", "The Federated States of Micronesia spans more than 2,500 kilometres of ocean from east to west.", "Federated_States_of_Micronesia"),
    ("Nauru", "NRU", "Oceania", "Yaren (seat of government; Nauru has no official capital)", -0.55, 166.92, "A small coral island in the central Pacific, just south of the equator.", "Nauru is the world's smallest island country and has no officially designated capital; government offices are in Yaren.", "Nauru"),
    ("New Zealand", "NZL", "Oceania", "Wellington", -41.29, 174.78, "Two main islands in the South Pacific, southeast of Australia across the Tasman Sea.", "New Zealand's Southern Alps run along much of the South Island and include Aoraki/Mount Cook, its highest peak.", "New_Zealand"),
    ("Palau", "PLW", "Oceania", "Ngerulmud", 7.50, 134.62, "An island country in the western Pacific, east of the Philippines.", "Palau's Rock Islands are hundreds of small, forested limestone islands surrounded by turquoise lagoons.", "Palau"),
    ("Papua New Guinea", "PNG", "Oceania", "Port Moresby", -9.44, 147.18, "On the eastern half of New Guinea, north of Australia, plus many nearby islands.", "Papua New Guinea is one of the world's most linguistically diverse countries, with more than 800 languages.", "Papua_New_Guinea"),
    ("Samoa", "WSM", "Oceania", "Apia", -13.83, -171.76, "A Polynesian island country in the South Pacific, northeast of Fiji.", "Samoa moved the International Date Line westward in 2011 so its calendar day would match key trading partners.", "Samoa"),
    ("Solomon Islands", "SLB", "Oceania", "Honiara", -9.43, 159.96, "An archipelago in the South Pacific east of Papua New Guinea.", "The Solomon Islands stretches across two island chains and hundreds of islands, many formed by volcanoes.", "Solomon_Islands"),
    ("Tonga", "TON", "Oceania", "Nuku'alofa", -21.14, -175.20, "A Polynesian kingdom of islands in the South Pacific, south of Samoa.", "Tonga is the only Pacific island monarchy never formally colonised by a European power.", "Tonga"),
    ("Tuvalu", "TUV", "Oceania", "Funafuti", -8.52, 179.20, "A chain of low coral atolls in the central Pacific, near the equator.", "Tuvalu is made up of nine low-lying islands and atolls, none more than a few metres above sea level.", "Tuvalu"),
    ("Vanuatu", "VUT", "Oceania", "Port Vila", -17.73, 168.32, "A volcanic island chain in the South Pacific, east of Australia and west of Fiji.", "Vanuatu has more than 80 islands, and several of its volcanoes are active.", "Vanuatu"),
]


# A short list of nationally important cities beyond the capital. The capital
# is added automatically, so small states can correctly have just one or two.
KEY_CITIES = {
    "Algeria": ["Oran", "Constantine"], "Angola": ["Huambo", "Lobito"], "Benin": ["Cotonou", "Parakou"],
    "Botswana": ["Francistown", "Maun"], "Burkina Faso": ["Bobo-Dioulasso", "Koudougou"], "Burundi": ["Bujumbura", "Ngozi"],
    "Cameroon": ["Douala", "Garoua"], "Chad": ["Moundou", "Abeche"], "Republic of the Congo": ["Pointe-Noire"],
    "Cote d'Ivoire": ["Abidjan", "Bouake"], "Democratic Republic of the Congo": ["Lubumbashi", "Mbuji-Mayi"],
    "Egypt": ["Alexandria", "Giza"], "Equatorial Guinea": ["Malabo", "Bata"], "Ethiopia": ["Dire Dawa", "Mekelle"],
    "Ghana": ["Kumasi", "Tamale"], "Kenya": ["Mombasa", "Kisumu"], "Madagascar": ["Toamasina", "Mahajanga"],
    "Morocco": ["Casablanca", "Marrakesh", "Fes"], "Mozambique": ["Beira", "Nampula"], "Nigeria": ["Lagos", "Kano", "Ibadan"],
    "Rwanda": ["Butare (Huye)", "Rubavu"], "Senegal": ["Touba", "Saint-Louis"], "South Africa": ["Cape Town", "Johannesburg"],
    "Sudan": ["Omdurman", "Port Sudan"], "Tanzania": ["Dar es Salaam", "Mwanza"], "Uganda": ["Entebbe", "Gulu"],
    "Zimbabwe": ["Bulawayo", "Mutare"], "China": ["Shanghai", "Guangzhou", "Chengdu"], "India": ["Mumbai", "Kolkata", "Chennai"],
    "Indonesia": ["Surabaya", "Bandung", "Medan"], "Iran": ["Mashhad", "Isfahan", "Shiraz"], "Iraq": ["Basra", "Mosul"],
    "Israel": ["Tel Aviv", "Haifa"], "Japan": ["Osaka", "Kyoto", "Yokohama"], "Kazakhstan": ["Almaty", "Shymkent"],
    "Malaysia": ["George Town", "Johor Bahru"], "Mongolia": ["Erdenet", "Darkhan"], "Nepal": ["Pokhara", "Lalitpur"],
    "Pakistan": ["Karachi", "Lahore", "Faisalabad"], "Philippines": ["Cebu City", "Davao City"], "Saudi Arabia": ["Jeddah", "Mecca", "Medina"],
    "South Korea": ["Busan", "Incheon", "Daegu"], "Sri Lanka": ["Colombo", "Kandy", "Galle"], "Thailand": ["Chiang Mai", "Pattaya"],
    "Turkey": ["Istanbul", "Izmir", "Bursa"], "United Arab Emirates": ["Dubai", "Sharjah"], "Vietnam": ["Ho Chi Minh City", "Da Nang", "Hue"],
    "Austria": ["Graz", "Salzburg"], "Belgium": ["Antwerp", "Ghent"], "Croatia": ["Split", "Dubrovnik"], "Czechia": ["Brno", "Ostrava"],
    "Denmark": ["Aarhus", "Odense"], "Finland": ["Tampere", "Turku"], "France": ["Marseille", "Lyon", "Bordeaux"],
    "Germany": ["Hamburg", "Munich", "Cologne"], "Greece": ["Thessaloniki", "Patras"], "Hungary": ["Debrecen", "Szeged"],
    "Ireland": ["Cork", "Galway"], "Italy": ["Milan", "Naples", "Florence"], "Netherlands": ["Rotterdam", "The Hague", "Utrecht"],
    "Norway": ["Bergen", "Trondheim"], "Poland": ["Krakow", "Gdansk", "Wroclaw"], "Portugal": ["Porto", "Coimbra"],
    "Romania": ["Cluj-Napoca", "Timisoara"], "Russia": ["Saint Petersburg", "Novosibirsk", "Vladivostok"], "Spain": ["Barcelona", "Seville", "Valencia"],
    "Sweden": ["Gothenburg", "Malmo"], "Switzerland": ["Geneva", "Basel", "Zurich"], "Ukraine": ["Kharkiv", "Odesa", "Lviv"],
    "United Kingdom": ["Manchester", "Edinburgh", "Birmingham"], "Canada": ["Toronto", "Montreal", "Vancouver"], "Mexico": ["Guadalajara", "Monterrey", "Puebla"],
    "United States": ["New York City", "Los Angeles", "Chicago"], "Brazil": ["Sao Paulo", "Rio de Janeiro", "Salvador"],
    "Argentina": ["Cordoba", "Rosario", "Mendoza"], "Chile": ["Valparaiso", "Concepcion"], "Colombia": ["Medellin", "Cali", "Cartagena"],
    "Peru": ["Arequipa", "Cusco", "Trujillo"], "Australia": ["Sydney", "Melbourne", "Brisbane"], "New Zealand": ["Auckland", "Christchurch", "Hamilton"],
    "Papua New Guinea": ["Lae", "Mount Hagen"],
}

# Common, useful international and regional organizations. Membership is
# represented as a compact list of names rather than a political description.
GROUPS = {
    "European Union": "Austria|Belgium|Bulgaria|Croatia|Cyprus|Czechia|Denmark|Estonia|Finland|France|Germany|Greece|Hungary|Ireland|Italy|Latvia|Lithuania|Luxembourg|Malta|Netherlands|Poland|Portugal|Romania|Slovakia|Slovenia|Spain|Sweden".split("|"),
    "NATO": "Albania|Belgium|Bulgaria|Canada|Croatia|Czechia|Denmark|Estonia|Finland|France|Germany|Greece|Hungary|Iceland|Italy|Latvia|Lithuania|Luxembourg|Montenegro|Netherlands|North Macedonia|Norway|Poland|Portugal|Romania|Slovakia|Slovenia|Spain|Sweden|Turkey|United Kingdom|United States".split("|"),
    "Commonwealth": "Antigua and Barbuda|Australia|Bahamas|Bangladesh|Barbados|Belize|Botswana|Brunei|Cameroon|Canada|Cyprus|Dominica|Eswatini|Fiji|Gabon|The Gambia|Ghana|Grenada|Guyana|India|Jamaica|Kenya|Kiribati|Lesotho|Malawi|Malaysia|Maldives|Malta|Mauritius|Mozambique|Namibia|Nauru|New Zealand|Nigeria|Pakistan|Papua New Guinea|Rwanda|Saint Kitts and Nevis|Saint Lucia|Saint Vincent and the Grenadines|Samoa|Seychelles|Sierra Leone|Singapore|Solomon Islands|South Africa|Sri Lanka|Tanzania|Togo|Tonga|Trinidad and Tobago|Tuvalu|Uganda|United Kingdom|Vanuatu|Zambia".split("|"),
    "ASEAN": "Brunei|Cambodia|Indonesia|Laos|Malaysia|Myanmar|Philippines|Singapore|Thailand|Timor-Leste|Vietnam".split("|"),
    "African Union": "Algeria|Angola|Benin|Botswana|Burkina Faso|Burundi|Cabo Verde|Cameroon|Central African Republic|Chad|Comoros|Cote d'Ivoire|Democratic Republic of the Congo|Djibouti|Egypt|Equatorial Guinea|Eritrea|Eswatini|Ethiopia|Gabon|The Gambia|Ghana|Guinea|Guinea-Bissau|Kenya|Lesotho|Liberia|Libya|Madagascar|Malawi|Mali|Mauritania|Mauritius|Morocco|Mozambique|Namibia|Niger|Nigeria|Rwanda|Sao Tome and Principe|Senegal|Seychelles|Sierra Leone|Somalia|South Africa|South Sudan|Sudan|Tanzania|Togo|Tunisia|Uganda|Zambia|Zimbabwe".split("|"),
    "Arab League": "Algeria|Bahrain|Comoros|Djibouti|Egypt|Iraq|Jordan|Kuwait|Lebanon|Libya|Mauritania|Morocco|Oman|Palestine|Qatar|Saudi Arabia|Somalia|Sudan|Syria|Tunisia|United Arab Emirates|Yemen".split("|"),
    "Gulf Cooperation Council": "Bahrain|Kuwait|Oman|Qatar|Saudi Arabia|United Arab Emirates".split("|"),
    "SAARC": "Afghanistan|Bangladesh|Bhutan|India|Maldives|Nepal|Pakistan|Sri Lanka".split("|"),
    "CARICOM": "Antigua and Barbuda|Bahamas|Barbados|Belize|Dominica|Grenada|Guyana|Haiti|Jamaica|Saint Kitts and Nevis|Saint Lucia|Saint Vincent and the Grenadines|Suriname|Trinidad and Tobago".split("|"),
    "East African Community": "Burundi|Democratic Republic of the Congo|Kenya|Rwanda|Somalia|South Sudan|Tanzania|Uganda".split("|"),
    "MERCOSUR": "Argentina|Bolivia|Brazil|Paraguay|Uruguay".split("|"),
    "G7": "Canada|France|Germany|Italy|Japan|United Kingdom|United States".split("|"),
    "G20": "Argentina|Australia|Brazil|Canada|China|France|Germany|India|Indonesia|Italy|Japan|Mexico|Russia|Saudi Arabia|South Africa|South Korea|Turkey|United Kingdom|United States".split("|"),
    "BRICS": "Brazil|Russia|India|China|South Africa|Saudi Arabia|Egypt|United Arab Emirates|Ethiopia|Iran|Indonesia".split("|"),
    "OECD": "Australia|Austria|Belgium|Canada|Chile|Colombia|Costa Rica|Czechia|Denmark|Estonia|Finland|France|Germany|Greece|Hungary|Iceland|Ireland|Israel|Italy|Japan|Latvia|Lithuania|Luxembourg|Mexico|Netherlands|New Zealand|Norway|Poland|Portugal|Slovakia|Slovenia|South Korea|Spain|Sweden|Switzerland|Turkey|United Kingdom|United States".split("|"),
    "OPEC": "Algeria|Republic of the Congo|Equatorial Guinea|Gabon|Iran|Iraq|Kuwait|Libya|Nigeria|Saudi Arabia|United Arab Emirates|Venezuela".split("|"),
}

GROUP_SOURCES = {
    "United Nations": ("United Nations member states", "https://www.un.org/about-us/member-states"),
    "United Nations (observer)": ("United Nations non-member observer states", "https://www.un.org/en/about-us/non-member-states"),
    "European Union": ("European Union countries", "https://european-union.europa.eu/principles-countries-history/eu-countries_en"),
    "NATO": ("NATO member countries", "https://www.nato.int/cps/en/natohq/topics_52044.htm"),
    "Commonwealth": ("Commonwealth member countries", "https://thecommonwealth.org/our-member-countries"),
    "ASEAN": ("ASEAN member states", "https://asean.org/member-states/"),
    "African Union": ("African Union member states", "https://au.int/en/member_states/countryprofiles2"),
    "Arab League": ("League of Arab States", "https://www.britannica.com/topic/Arab-League"),
    "Gulf Cooperation Council": ("Gulf Cooperation Council member states", "https://www.gcc-sg.org/en/AboutUs/MemberStates/Pages/Home.aspx"),
    "SAARC": ("SAARC member states", "https://www.saarc-sec.org/index.php/about-saarc/about-saarc"),
    "CARICOM": ("CARICOM member states", "https://caricom.org/member-states-and-associate-members/"),
    "East African Community": ("East African Community partner states", "https://www.eac.int/eac-partner-states/"),
    "MERCOSUR": ("MERCOSUR member states", "https://www.mercosur.int/en/about-mercosur/mercosur-countries/"),
    "G7": ("G7 members", "https://www.g7italy.it/en/g7/"), "G20": ("G20 members", "https://www.g20.org/en/about-the-g20"),
    "BRICS": ("BRICS members", "https://brics.br/en/about-the-brics"), "OECD": ("OECD members", "https://www.oecd.org/en/about/members-partners.html"),
    "OPEC": ("OPEC member countries", "https://www.opec.org/member-countries.html"),
}

# ISO 3166-1 alpha-2 codes used by FlagCDN. The country records already use
# alpha-3 IDs for the map; keep the flag service's two-letter code alongside it.
FLAG_CODES = dict(item.split(":") for item in """
dza:dz ago:ao ben:bj bwa:bw bfa:bf bdi:bi cpv:cv cmr:cm caf:cf tcd:td com:km cog:cg civ:ci cod:cd dji:dj egy:eg gnq:gq eri:er swz:sz eth:et gab:ga gmb:gm gha:gh gin:gn gnb:gw ken:ke lso:ls lbr:lr lby:ly mdg:mg mwi:mw mli:ml mrt:mr mus:mu mar:ma moz:mz nam:na ner:ne nga:ng rwa:rw stp:st sen:sn syc:sc sle:sl som:so zaf:za ssd:ss sdn:sd tza:tz tgo:tg tun:tn uga:ug zmb:zm zwe:zw afg:af arm:am aze:az bhr:bh bgd:bd btn:bt brn:bn khm:kh chn:cn cyp:cy geo:ge ind:in idn:id irn:ir irq:iq isr:il jpn:jp jor:jo kaz:kz kwt:kw kgz:kg lao:la lbn:lb mys:my mdv:mv mng:mn mmr:mm npl:np prk:kp omn:om pak:pk pse:ps phl:ph qat:qa sau:sa sgp:sg kor:kr lka:lk syr:sy tjk:tj tha:th tls:tl tur:tr tkm:tm are:ae uzb:uz vnm:vn yem:ye alb:al and:ad aut:at blr:by bel:be bih:ba bgr:bg hrv:hr cze:cz dnk:dk est:ee fin:fi fra:fr deu:de grc:gr vat:va hun:hu isl:is irl:ie ita:it lva:lv lie:li ltu:lt lux:lu mlt:mt mda:md mco:mc mne:me nld:nl mkd:mk nor:no pol:pl prt:pt rou:ro rus:ru smr:sm srb:rs svk:sk svn:si esp:es swe:se che:ch ukr:ua gbr:gb atg:ag arg:ar bhs:bs brb:bb blz:bz bol:bo bra:br can:ca chl:cl col:co cri:cr cub:cu dma:dm dom:do ecu:ec slv:sv grd:gd gtm:gt guy:gy hti:ht hnd:hn jam:jm mex:mx nic:ni pan:pa pry:py per:pe kna:kn lca:lc vct:vc sur:sr tto:tt usa:us ury:uy ven:ve aus:au fji:fj kir:ki mhl:mh fsm:fm nru:nr nzl:nz plw:pw png:pg wsm:ws slb:sb ton:to tuv:tv vut:vu
""".split())

def make_record(seed):
    name, code, region, capital, lat, lon, location, fact, slug = seed
    sources = [{
        "title": f"{name} — geography and country overview",
        "url": f"https://en.wikipedia.org/wiki/{quote(slug, safe='_()')}",
    }]
    if code == "GNQ":
        sources.append({
            "title": "Equatorial Guinea government decree on Ciudad de la Paz",
            "url": "https://www.guineaecuatorialpress.com/noticias/decreto_ley_por_el_que_se_declara_la_ciudad_de_la_paz_djibloho_capital_de_la_republica_de_guinea_ecuatorial",
        })
    cities = [capital.split(" (")[0]]
    cities.extend(KEY_CITIES.get(name, []))
    memberships = ["United Nations"] if code not in {"VAT", "PSE"} else ["United Nations (observer)" ]
    for group, members in GROUPS.items():
        if name in members:
            memberships.append(group)
    return {
        "id": code.lower(),
        "flagCode": FLAG_CODES[code.lower()],
        "country": name,
        "region": region,
        "capital": capital,
        "keyCities": list(dict.fromkeys(cities)),
        "memberships": memberships,
        "membershipSources": [
            {"group": group, "title": GROUP_SOURCES[group][0], "url": GROUP_SOURCES[group][1]}
            for group in memberships
        ],
        "location": {"summary": location, "latitude": lat, "longitude": lon},
        "fact": {"text": fact, "context": "The map marker is placed near the capital to help you find the country."},
        "question": {
            "text": f"What is one memorable geography detail about {name}?",
            "answer": fact,
        },
        "sources": sources,
    }


if __name__ == "__main__":
    records = [make_record(seed) for seed in SEEDS]
    expected_regions = {"Africa": 54, "Asia": 48, "Europe": 44, "Americas": 35, "Oceania": 14}
    actual_regions = {region: sum(row[2] == region for row in SEEDS) for region in expected_regions}
    assert len(records) == 195, f"Expected 195 sovereign-state entries; found {len(records)}"
    assert len({row[1] for row in SEEDS}) == len(SEEDS), "Duplicate ISO country code"
    assert actual_regions == expected_regions, f"Country coverage differs: {actual_regions}"
    for record in records:
        assert record["fact"]["text"] and record["location"]["summary"]
        assert -90 <= record["location"]["latitude"] <= 90
        assert -180 <= record["location"]["longitude"] <= 180
        assert record["sources"] and all(source["url"].startswith("https://") for source in record["sources"])
    Path("countries.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} country entries")
