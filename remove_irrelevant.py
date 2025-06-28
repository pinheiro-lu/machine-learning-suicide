import re

series_names_to_exclude = [
    # **Environmental/Resource-Specific (Indirect Relevance, often outcomes/very specific):**
    'Adjusted net savings, excluding particulate emission damage (% of GNI)',
    'Adjusted net savings, excluding particulate emission damage (current US$)',
    'Adjusted net savings, including particulate emission damage (% of GNI)',
    'Adjusted net savings, including particulate emission damage (current US$)',
    'Adjusted savings: carbon dioxide damage (% of GNI)',
    'Adjusted savings: carbon dioxide damage (current US$)',
    'Adjusted savings: consumption of fixed capital (% of GNI)',
    'Adjusted savings: consumption of fixed capital (current US$)',
    'Adjusted savings: education expenditure (% of GNI)', # Keep education expenditure (actual), but not its "savings" context
    'Adjusted savings: education expenditure (current US$)',
    'Adjusted savings: energy depletion (% of GNI)',
    'Adjusted savings: energy depletion (current US$)',
    'Adjusted savings: gross savings (% of GNI)',
    'Adjusted savings: mineral depletion (% of GNI)',
    'Adjusted savings: mineral depletion (current US$)',
    'Adjusted savings: natural resources depletion (% of GNI)',
    'Adjusted savings: net national savings (% of GNI)',
    'Adjusted savings: net national savings (current US$)',
    'Adjusted savings: particulate emission damage (% of GNI)',
    'Adjusted savings: particulate emission damage (current US$)',
    'Agriculture, forestry, and fishing, value added per worker (constant 2015 US$)', # Keep general value added, but per worker is granular
    'Air transport, freight (million ton-km)',
    'Air transport, passengers carried',
    'Air transport, registered carrier departures worldwide',
    'Alternative and nuclear energy (% of total energy use)',
    'Annual freshwater withdrawals, agriculture (% of total freshwater withdrawal)',
    'Annual freshwater withdrawals, domestic (% of total freshwater withdrawal)',
    'Annual freshwater withdrawals, industry (% of total freshwater withdrawal)',
    'Annual freshwater withdrawals, total (% of internal resources)',
    'Annual freshwater withdrawals, total (billion cubic meters)',
    'Aquaculture production (metric tons)',
    'Cereal production (metric tons)',
    'Cereal yield (kg per hectare)',
    'Coal rents (% of GDP)',
    'Carbon intensity of GDP (kg CO2e per 2021 PPP $ of GDP)',
    'Carbon intensity of GDP (kg CO2e per constant 2015 US$ of GDP)',
    'Carbon dioxide (CO2) net fluxes from LULUCF - Total excluding non-tropical fires (Mt CO2e)',
    'Carbon dioxide (CO2) emissions excluding LULUCF per capita (t CO2e/capita)',
    'Carbon dioxide (CO2) emissions (total) excluding LULUCF (Mt CO2e)',
    'Carbon dioxide (CO2) emissions (total) excluding LULUCF (% change from 1990)',
    'Electric power transmission and distribution losses (% of output)', # Too specific for infrastructure
    'Electric power consumption (kWh per capita)', # Energy consumption is indirect for socioeconomic drivers of suicide
    'Fish species, threatened',
    'Food production index (2014-2016 = 100)',
    'Food, beverages and tobacco (% of value added in manufacturing)',
    'GDP per unit of energy use (constant 2021 PPP $ per kg of oil equivalent)',
    'GDP per unit of energy use (PPP $ per kg of oil equivalent)',
    'Total natural resources rents (% of GDP)', # Too broad for specific resource impact

    # **Very Granular/Specific Socioeconomic Breakdowns (Redundant given broader indicators):**
    # Keep the overall 'Access to electricity (% of population)' but remove specific rural/urban
    'Access to electricity, rural (% of rural population)',
    'Access to electricity, urban (% of urban population)',
    # Keep general 'Account ownership' but remove all specific age/gender/income/education breakdowns
    'Account ownership at a financial institution or with a mobile-money-service provider, female (% of population ages 15+)',
    'Account ownership at a financial institution or with a mobile-money-service provider, male (% of population ages 15+)',
    'Account ownership at a financial institution or with a mobile-money-service provider, older adults (% of population ages 25+)',
    'Account ownership at a financial institution or with a mobile-money-service provider, poorest 40% (% of population ages 15+)',
    'Account ownership at a financial institution or with a mobile-money-service provider, primary education or less (% of population ages 15+)',
    'Account ownership at a financial institution or with a mobile-money-service provider, richest 60% (% of population ages 15+)',
    'Account ownership at a financial institution or with a mobile-money-service provider, secondary education or more (% of population ages 15+)',
    'Account ownership at a financial institution or with a mobile-money-service provider, young adults (% of population ages 15-24)',
    # Adequacy of social programs - Keep the overall coverage instead of adequacy of specific programs
    'Adequacy of social insurance programs (% of total welfare of beneficiary households)',
    'Adequacy of social protection and labor programs (% of total welfare of beneficiary households)',
    'Adequacy of social safety net programs (% of total welfare of beneficiary households)',
    'Adequacy of unemployment benefits and ALMP (% of total welfare of beneficiary households)',
    # Adjusted net enrollment rate - Keep main enrollment, these are too detailed/adjusted
    'Adjusted net enrollment rate, primary (% of primary school age children)',
    'Adjusted net enrollment rate, primary, female (% of primary school age children)',
    'Adjusted net enrollment rate, primary, male (% of primary school age children)',
    # Children in employment - These are outcomes/very specific. Broader poverty/education indicators are better.
    'Average working hours of children, study and work, ages 7-14 (hours per week)',
    'Average working hours of children, study and work, female, ages 7-14 (hours per week)',
    'Average working hours of children, study and work, male, ages 7-14 (hours per week)',
    'Average working hours of children, working only, ages 7-14 (hours per week)',
    'Average working hours of children, working only, female, ages 7-14 (hours per week)',
    'Average working hours of children, working only, male, ages 7-14 (hours per week)',
    'Children in employment, female (% of female children ages 7-14)',
    'Children in employment, male (% of male children ages 7-14)',
    'Children in employment, self-employed (% of children in employment, ages 7-14)',
    'Children in employment, self-employed, female (% of female children in employment, ages 7-14)',
    'Children in employment, self-employed, male (% of male children in employment, ages 7-14)',
    'Children in employment, study and work (% of children in employment, ages 7-14)',
    'Children in employment, study and work, female (% of female children in employment, ages 7-14)',
    'Children in employment, study and work, male (% of children in employment, ages 7-14)',
    'Children in employment, total (% of children ages 7-14)',
    'Children in employment, unpaid family workers (% of children in employment, ages 7-14)',
    'Children in employment, unpaid family workers, female (% of female children in employment, ages 7-14)',
    'Children in employment, unpaid family workers, male (% of male children in employment, ages 7-14)',
    'Children in employment, wage workers (% of children in employment, ages 7-14)',
    'Children in employment, wage workers, female (% of female children in employment, ages 7-14)',
    'Children in employment, wage workers, male (% of male children in employment, ages 7-14)',
    'Children in employment, work only (% of children in employment, ages 7-14)',
    'Children in employment, work only, female (% of female children in employment, ages 7-14)',
    'Children in employment, work only, male (% of male children in employment, ages 7-14)',
    # Contribution family workers - keep overall employment ratios.
    'Contributing family workers, female (% of female employment) (modeled ILO estimate)',
    'Contributing family workers, male (% of male employment) (modeled ILO estimate)',
    'Contributing family workers, total (% of total employment) (modeled ILO estimate)',
    # Coverage of social programs - Keep the general coverage, remove detailed quintile breakdowns for simplicity
    'Coverage of social insurance programs in 2nd quintile (% of population)',
    'Coverage of social insurance programs in 3rd quintile (% of population)',
    'Coverage of social insurance programs in 4th quintile (% of population)',
    'Coverage of social insurance programs in poorest quintile (% of population)',
    'Coverage of social insurance programs in richest quintile (% of population)',
    'Coverage of social safety net programs in 2nd quintile (% of population)',
    'Coverage of social safety net programs in 3rd quintile (% of population)',
    'Coverage of social safety net programs in 4th quintile (% of population)',
    'Coverage of social safety net programs in poorest quintile (% of population)',
    'Coverage of social safety net programs in richest quintile (% of population)',
    'Coverage of unemployment benefits and ALMP in 2nd quintile (% of population)',
    'Coverage of unemployment benefits and ALMP in 3rd quintile (% of population)',
    'Coverage of unemployment benefits and ALMP in 4th quintile (% of population)',
    'Coverage of unemployment benefits and ALMP in poorest quintile (% of population)',
    'Coverage of unemployment benefits and ALMP in richest quintile (% of population)',
    # Current education expenditure - Keep total or % of GDP, remove detailed institution type
    'Current education expenditure, primary (% of total expenditure in primary public institutions)',
    'Current education expenditure, secondary (% of total expenditure in secondary public institutions)',
    'Current education expenditure, tertiary (% of total expenditure in tertiary public institutions)',
    # Detailed Employment Ratios by Age/Gender/ILO model - Keep overall total, female, male. Too many granularities.
    'Employers, female (% of female employment) (modeled ILO estimate)',
    'Employers, male (% of male employment) (modeled ILO estimate)',
    'Employers, total (% of total employment) (modeled ILO estimate)',
    'Employment in agriculture, female (% of female employment) (modeled ILO estimate)',
    'Employment in agriculture, male (% of male employment) (modeled ILO estimate)',
    'Employment in industry, female (% of female employment) (modeled ILO estimate)',
    'Employment in industry, male (% of male employment) (modeled ILO estimate)',
    'Employment in services, female (% of female employment) (modeled ILO estimate)',
    'Employment in services, male (% of male employment) (modeled ILO estimate)',
    'Employment to population ratio, 15+, female (%) (modeled ILO estimate)',
    'Employment to population ratio, 15+, female (%) (national estimate)',
    'Employment to population ratio, 15+, male (%) (modeled ILO estimate)',
    'Employment to population ratio, 15+, male (%) (national estimate)',
    'Employment to population ratio, ages 15-24, female (%) (modeled ILO estimate)',
    'Employment to population ratio, ages 15-24, female (%) (national estimate)',
    'Employment to population ratio, ages 15-24, male (%) (modeled ILO estimate)',
    'Employment to population ratio, ages 15-24, male (%) (national estimate)',
    'Employment to population ratio, ages 15-24, total (%) (modeled ILO estimate)',
    'Employment to population ratio, ages 15-24, total (%) (national estimate)',
    'Labor force participation rate for ages 15-24, female (%) (modeled ILO estimate)',
    'Labor force participation rate for ages 15-24, female (%) (national estimate)',
    'Labor force participation rate for ages 15-24, male (%) (modeled ILO estimate)',
    'Labor force participation rate for ages 15-24, male (%) (national estimate)',
    'Labor force participation rate for ages 15-24, total (%) (modeled ILO estimate)',
    'Labor force participation rate for ages 15-24, total (%) (national estimate)',
    'Labor force participation rate, female (% of female population ages 15+) (modeled ILO estimate)',
    'Labor force participation rate, female (% of female population ages 15+) (national estimate)',
    'Labor force participation rate, female (% of female population ages 15-64) (modeled ILO estimate)',
    'Labor force participation rate, male (% of male population ages 15+) (modeled ILO estimate)',
    'Labor force participation rate, male (% of male population ages 15+) (national estimate)',
    'Labor force participation rate, male (% of male population ages 15-64) (modeled ILO estimate)',
    'Labor force participation rate, total (% of total population ages 15+) (modeled ILO estimate)',
    'Labor force participation rate, total (% of total population ages 15+) (national estimate)',
    'Labor force participation rate, total (% of total population ages 15-64) (modeled ILO estimate)',
    'Labor force with advanced education (% of total working-age population with advanced education)',
    'Labor force with advanced education, female (% of female working-age population with advanced education)',
    'Labor force with advanced education, male (% of male working-age population with advanced education)',
    'Labor force with basic education (% of total working-age population with basic education)',
    'Labor force with basic education, female (% of female working-age population with basic education)',
    'Labor force with basic education, male (% of male working-age population with basic education)',
    'Labor force with intermediate education (% of total working-age population with intermediate education)',
    'Labor force with intermediate education, female (% of female working-age population with intermediate education)',
    'Labor force with intermediate education, male (% of male working-age population with advanced education)',
    'Unemployment with advanced education (% of total labor force with advanced education)',
    'Unemployment with advanced education, female (% of female labor force with advanced education)',
    'Unemployment with advanced education, male (% of male labor force with advanced education)',
    'Unemployment with basic education (% of total labor force with basic education)',
    'Unemployment with basic education, female (% of female labor force with basic education)',
    'Unemployment with basic education, male (% of male labor force with basic education)',
    'Unemployment with intermediate education (% of total labor force with intermediate education)',
    'Unemployment with intermediate education, female (% of female labor force with intermediate education)',
    'Unemployment with intermediate education, male (% of male labor force with intermediate education)',
    'Unemployment, female (% of female labor force) (modeled ILO estimate)',
    'Unemployment, female (% of female labor force) (national estimate)',
    'Unemployment, male (% of male labor force) (modeled ILO estimate)',
    'Unemployment, male (% of male labor force) (national estimate)',
    'Unemployment, youth female (% of female labor force ages 15-24) (modeled ILO estimate)',
    'Unemployment, youth female (% of female labor force ages 15-24) (national estimate)',
    'Unemployment, youth male (% of male labor force ages 15-24) (modeled ILO estimate)',
    'Unemployment, youth male (% of male labor force ages 15-24) (national estimate)',
    'Unemployment, youth total (% of total labor force ages 15-24) (modeled ILO estimate)',
    'Unemployment, youth total (% of total labor force ages 15-24) (national estimate)',
    'Vulnerable employment, female (% of female employment) (modeled ILO estimate)',
    'Vulnerable employment, male (% of male employment) (modeled ILO estimate)',
    'Vulnerable employment, total (% of total employment) (modeled ILO estimate)',
    'Wage and salaried workers, female (% of female employment) (modeled ILO estimate)',
    'Wage and salaried workers, male (% of male employment) (modeled ILO estimate)',
    'Wage and salaried workers, total (% of total employment) (modeled ILO estimate)',
    # Population Ages Breakdowns - Keep general age dependency, population total, and broad age groups if needed, but not all minute % breakdowns.
    'Population ages 00-04, female (% of female population)',
    'Population ages 00-04, male (% of male population)',
    'Population ages 0-14, female',
    'Population ages 0-14, female (% of female population)',
    'Population ages 0-14, male',
    'Population ages 0-14, male (% of male population)',
    'Population ages 05-09, female (% of female population)',
    'Population ages 05-09, male (% of male population)',
    'Population ages 10-14, female (% of female population)',
    'Population ages 10-14, male (% of male population)',
    'Population ages 15-19, female (% of female population)',
    'Population ages 15-19, male (% of male population)',
    'Population ages 15-64, female',
    'Population ages 15-64, female (% of female population)',
    'Population ages 15-64, male',
    'Population ages 15-64, male (% of male population)',
    'Population ages 20-24, female (% of female population)',
    'Population ages 20-24, male (% of male population)',
    'Population ages 25-29, female (% of female population)',
    'Population ages 25-29, male (% of male population)',
    'Population ages 30-34, female (% of female population)',
    'Population ages 30-34, male (% of male population)',
    'Population ages 35-39, female (% of female population)',
    'Population ages 35-39, male (% of male population)',
    'Population ages 40-44, female (% of female population)',
    'Population ages 40-44, male (% of male population)',
    'Population ages 45-49, female (% of female population)',
    'Population ages 45-49, male (% of male population)',
    'Population ages 50-54, female (% of female population)',
    'Population ages 50-54, male (% of male population)',
    'Population ages 55-59, female (% of female population)',
    'Population ages 55-59, male (% of male population)',
    'Population ages 60-64, female (% of female population)',
    'Population ages 60-64, male (% of male population)',
    'Population ages 65 and above, female',
    'Population ages 65 and above, female (% of female population)',
    'Population ages 65 and above, male',
    'Population ages 65 and above, male (% of male population)',
    'Population ages 65-69, female (% of female population)',
    'Population ages 65-69, male (% of male population)',
    'Population ages 70-74, female (% of female population)',
    'Population ages 70-74, male (% of male population)',
    'Population ages 75-79, female (% of female population)',
    'Population ages 75-79, male (% of male population)',
    'Population ages 80 and above, female (% of female population)',
    'Population ages 80 and above, male (% of male population)',
    'Female primary school age children out-of-school (%)',
    'Male primary school age children out-of-school (%)',
    'Learning poverty: Share of Children at the End-of-Primary age below minimum reading proficiency adjusted by Out-of-School Children (%)',
    'Learning poverty: Share of Female Children at the End-of-Primary age below minimum reading proficiency adjusted by Out-of-School Children (%)',
    'Learning poverty: Share of Male Children at the End-of-Primary age below minimum reading proficiency adjusted by Out-of-School Children (%)',
    'Literacy rate, youth (ages 15-24), gender parity index (GPI)', # Keep general literacy rates
    'Literacy rate, youth female (% of females ages 15-24)',
    'Literacy rate, youth male (% of males ages 15-24)',
    'Literacy rate, youth total (% of people ages 15-24)',
    'Lower secondary school starting age (years)',
    'Primary education, pupils (% female)',
    'Primary education, teachers (% female)',
    'Primary education, duration (years)',
    'Preprimary education, duration (years)',
    'Primary school starting age (years)',
    'Secondary education, duration (years)',
    'Secondary education, pupils (% female)',
    'Secondary education, pupils',
    'Tertiary education, academic staff (% female)',

    # **Governance/Financial Stability Ratings (Often highly correlated with broader economic/political stability indices):**
    'Control of Corruption: Number of Sources',
    'Control of Corruption: Percentile Rank, Lower Bound of 90% Confidence Interval',
    'Control of Corruption: Percentile Rank, Upper Bound of 90% Confidence Interval',
    'Control of Corruption: Standard Error',
    'Government Effectiveness: Number of Sources',
    'Government Effectiveness: Percentile Rank, Lower Bound of 90% Confidence Interval',
    'Government Effectiveness: Percentile Rank, Upper Bound of 90% Confidence Interval',
    'Government Effectiveness: Standard Error',
    'Regulatory Quality: Number of Sources',
    'Regulatory Quality: Percentile Rank, Lower Bound of 90% Confidence Interval',
    'Regulatory Quality: Percentile Rank, Upper Bound of 90% Confidence Interval',
    'Regulatory Quality: Standard Error',
    'Rule of Law: Number of Sources',
    'Rule of Law: Percentile Rank, Lower Bound of 90% Confidence Interval',
    'Rule of Law: Percentile Rank, Upper Bound of 90% Confidence Interval',
    'Rule of Law: Standard Error',
    'Voice and Accountability: Number of Sources',
    'Voice and Accountability: Percentile Rank, Lower Bound of 90% Confidence Interval',
    'Voice and Accountability: Percentile Rank, Upper Bound of 90% Confidence Interval',
    'Voice and Accountability: Standard Error',
    'Statistical performance indicators (SPI): Overall score (scale 0-100)', # These are about data quality, not socioeconomic conditions
    'Statistical performance indicators (SPI): Pillar 1 data use score (scale 0-100)',
    'Statistical performance indicators (SPI): Pillar 2 data services score (scale 0-100)',
    'Statistical performance indicators (SPI): Pillar 3 data products score (scale 0-100)',
    'Statistical performance indicators (SPI): Pillar 4 data sources score (scale 0-100)',
    'Statistical performance indicators (SPI): Pillar 5 data infrastructure score (scale 0-100)',
    'Disaster risk reduction progress score (1-5 scale; 5=best)', # Environmental risk, not core socioeconomic
    'Number of visits or required meetings with tax officials (average for affected firms)', # Too specific business metric

    # **Very Specific Business/Financial Details (Redundant with broader economic indicators):**
    'Changes in inventories (constant LCU)',
    'Changes in inventories (current LCU)',
    'Changes in inventories (current US$)',
    'Computer, communications and other services (% of commercial service exports)',
    'Computer, communications and other services (% of commercial service imports)',
    'Fixed broadband subscriptions', # Keep per 100 people, remove raw count
    'Fixed telephone subscriptions', # Keep per 100 people, remove raw count
    'Foreign direct investment, net (BoP, current US$)', # Keep % of GDP, remove raw current US$
    'Foreign direct investment, net inflows (BoP, current US$)',
    'Foreign direct investment, net outflows (BoP, current US$)',
    'GDP deflator (base year varies by country)', # Highly correlated with inflation, GDP current vs constant captures this
    'GDP deflator: linked series (base year varies by country)',
    'GDP: linked series (current LCU)',
    'GNI: linked series (current LCU)',
    'Gross capital formation (constant LCU)', # Keep GDP %, and one constant/current US$ version
    'Gross capital formation (current LCU)',
    'Gross domestic income (constant LCU)',
    'Gross domestic savings (current LCU)',
    'Gross domestic savings (current US$)',
    'Gross fixed capital formation (constant LCU)', # Keep GDP %, and one constant/current US$ version
    'Gross fixed capital formation (current LCU)',
    'Gross fixed capital formation, private sector (current LCU)',
    'High-technology exports (current US$)', # Keep % of manufactured exports if desired, remove raw US$
    'Industrial design applications, nonresident, by count',
    'Industrial design applications, resident, by count',
    'Industry (including construction), value added per worker (constant 2015 US$)',
    'Inflation, GDP deflator (annual %)', # Keep CPI inflation
    'Inflation, GDP deflator: linked series (annual %)',
    'Manufacturing, value added (constant LCU)', # Keep % of GDP and one constant/current US$
    'Manufacturing, value added (current LCU)',
    'Multilateral debt service (TDS, current US$)', # Debt service % of GNI/exports is more useful
    'Net official aid received (constant 2021 US$)', # Keep current US$
    'Present value of external debt (% of exports of goods, services and primary income)', # Keep % of GNI
    'Scientific and technical journal articles', # R&D is a better indicator
    'Services, value added (constant LCU)', # Keep % of GDP and one constant/current US$
    'Services, value added (current LCU)',
    'Services, value added per worker (constant 2015 US$)',
    'Stocks traded, turnover ratio of domestic shares (%)', # Too specific for financial market health
    'Gross capital formation (current US$)', # Keeping other GDP related, this adds less unique info
    'Gross capital formation (annual % growth)',
    'Gross capital formation (constant 2015 US$)',
    'Gross fixed capital formation (% of GDP)',
    'Gross fixed capital formation (annual % growth)',
    'Gross fixed capital formation (constant 2015 US$)',
    'Gross fixed capital formation (constant LCU)',
    'Gross fixed capital formation (current LCU)',
    'Gross fixed capital formation (current US$)',
    'Gross fixed capital formation, private sector (% of GDP)',
    'Gross fixed capital formation, private sector (current LCU)',
    'Gross savings (current LCU)',
    'Gross savings (current US$)',

    # **Health Outcomes/Behavior (often outcomes, not determinants for *this* study):**
    'Contraceptive prevalence, any method (% of married women ages 15-49)', # Behavioral/health outcome
    'PM2.5 air pollution, mean annual exposure (micrograms per cubic meter)', # Environmental health outcome
    'PM2.5 air pollution, population exposed to levels exceeding WHO guideline value (% of total)',
    'PM2.5 pollution, population exposed to levels exceeding WHO Interim Target-1 value (% of total)',
    'PM2.5 pollution, population exposed to levels exceeding WHO Interim Target-2 value (% of total)',
    'PM2.5 pollution, population exposed to levels exceeding WHO Interim Target-3 value (% of total)',

    # **Political Stability/Human Rights Details (keep overall estimate, remove components):**
    'Political Stability and Absence of Violence/Terrorism: Number of Sources',
    'Political Stability and Absence of Violence/Terrorism: Percentile Rank, Lower Bound of 90% Confidence Interval',
    'Political Stability and Absence of Violence/Terrorism: Percentile Rank, Upper Bound of 90% Confidence Interval',
    'Political Stability and Absence of Violence/Terrorism: Standard Error',
    'Proportion of women subjected to physical and/or sexual violence in the last 12 months (% of ever-partnered women ages 15-49)', # Important social issue, but maybe too specific for broad socioeconomic determinants
    'Women who were first married by age 15 (% of women ages 20-24)',
    'Women who were first married by age 18 (% of women ages 20-24)',
    'Proportion of time spent on unpaid domestic and care work, female (% of 24 hour day)',
    'Proportion of time spent on unpaid domestic and care work, male (% of 24 hour day)',
    'Asylum-seekers by country or territory of asylum', # Related to conflict/migration, not core socioeconomic
    'International migrant stock (% of population)',
    'International migrant stock, total',
    'Net migration',
    'Rural population living in areas where elevation is below 5 meters (% of total population)',
    'Urban population living in areas where elevation is below 5 meters (% of total population)',
    'Population living in areas where elevation is below 5 meters (% of total population)',
    'Rural population', # Keep % of total, remove raw count
    'Urban population', # Keep % of total, remove raw count

    # **Redundant/Less Informative for General Socioeconomic Trends:**
    'Adjusted net national income (annual % growth)', # Keep per capita
    'Adjusted net national income (constant 2015 US$)',
    'Adjusted net national income (current US$)',
    'Agriculture, forestry, and fishing, value added (annual % growth)', # Keep % of GDP, constant/current US$
    'Agriculture, forestry, and fishing, value added (constant LCU)',
    'Agriculture, forestry, and fishing, value added (current LCU)',
    'Central government debt, total (current LCU)', # Keep % of GDP
    'Compensation of employees (current LCU)', # Keep % of expense or GDP version if available
    'Current health expenditure per capita (current US$)', # Keep % of GDP and PPP version
    'Domestic general government health expenditure per capita (current US$)', # Keep % of GDP and PPP version
    'Domestic private health expenditure per capita (current US$)', # Keep % of GDP and PPP version
    'Expense (current LCU)', # Keep % of GDP
    'Final consumption expenditure (annual % growth)', # Keep % of GDP, constant/current US$
    'Final consumption expenditure (constant LCU)',
    'Final consumption expenditure (current LCU)',
    'Final consumption expenditure (current US$)',
    'Foreign direct investment, net inflows (% of GDP)', # Keep this
    'Foreign direct investment, net inflows (BoP, current US$)',
    'Foreign direct investment, net outflows (% of GDP)', # Keep this
    'Foreign direct investment, net outflows (BoP, current US$)',
    'GDP (constant LCU)',
    'GDP (current LCU)',
    'GDP per capita (constant LCU)',
    'GDP per capita (current LCU)',
    'General government final consumption expenditure (annual % growth)', # Keep % of GDP, constant/current US$
    'General government final consumption expenditure (constant LCU)',
    'General government final consumption expenditure (current LCU)',
    'GNI (constant LCU)',
    'GNI (current LCU)',
    'GNI per capita (constant LCU)',
    'GNI per capita (current LCU)',
    'Gross capital formation (current LCU)',
    'Gross domestic savings (current LCU)',
    'Gross fixed capital formation (current LCU)',
    'Industry (including construction), value added (annual % growth)', # Keep % of GDP, constant/current US$
    'Industry (including construction), value added (constant LCU)',
    'Industry (including construction), value added (current LCU)',
    'Manufacturing, value added (annual % growth)', # Keep % of GDP, constant/current US$
    'Manufacturing, value added (constant LCU)',
    'Manufacturing, value added (current LCU)',
    'Net official aid received (current US$)', # Keep constant US$ or % of GNI
    'Out-of-pocket expenditure per capita (current US$)', # Keep % of current health expenditure and PPP version
    'Personal remittances, paid (current US$)', # Keep received % of GDP and received current US$
    'Personal transfers, receipts (BoP, current US$)',
    'Population ages 0-14, total',
    'Population ages 15-64, total',
    'Population ages 65 and above, total',
    'Population, female',
    'Population, male',
    'Population, total', # Keep Population density and Population growth
    'Rural population growth (annual %)',
    'Services, value added (annual % growth)', # Keep % of GDP, constant/current US$
    'Services, value added (constant LCU)',
    'Services, value added (current LCU)',
    'Unemployment, total (% of total labor force) (modeled ILO estimate)', # Keep national estimate
    'Urban population growth (annual %)',
    'Female headed households (% of households with a female head)', # Too specific on household structure
    'Fixed broadband subscriptions',
    'Fixed telephone subscriptions',
    'GNI per capita, Atlas method (current US$)',
    'GNI, Atlas method (current US$)',
    'Population in largest city',
    'Poverty headcount ratio at $3.00 a day (2021 PPP) (% of population)', # Keep national/societal poverty for more context
    'Poverty headcount ratio at $4.20 a day (2021 PPP) (% of population)',
    'Poverty headcount ratio at $8.30 a day (2021 PPP) (% of population)',
    'Net official aid received (constant 2021 US$)',
    'Stocks traded, turnover ratio of domestic shares (%)',
    'Prosperity gap (average shortfall from a prosperity standard of $28/day)',
    'Present value of external debt (% of exports of goods, services and primary income)',
    'Public and publicly guaranteed debt service (% of exports of goods, services and primary income)', # Keep % of GNI
    'Scientific and technical journal articles',
    'Population in the largest city (% of urban population)',
    'Population in urban agglomerations of more than 1 million',
    'Population in urban agglomerations of more than 1 million (% of total population)',
    'Rural population',
    'Urban population',
    'nan', # Remove the 'nan' entry if it appeared due to data parsing.
]

# Read the unique series names from unique.txt
with open('unique.txt', 'r') as file:
    initial_series_names = file.read().strip().split('\n')

# Remove normalization logic and directly compare series names
filtered_series_names = [name for name in initial_series_names if name not in series_names_to_exclude]

print(f"I have {len(filtered_series_names)} series after removing the specified ones.")
print(f"Tried to remove {len(series_names_to_exclude)} series.")

# Save the filtered series names to a file
with open('filtered_series_names.txt', 'w') as file:
    file.write('\n'.join(filtered_series_names))