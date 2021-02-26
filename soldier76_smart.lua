-- internal configuration
userInfo = {
    -- Whether to output debugging information, the CPU calculation pressure can be reduced after close.
	-- It is recommended to turn it on during debugging and turn it off after debugging.
	-- (0 - Disable | 1 - Enable)
	debug = 1,
	-- Sensitivity adjustment
    sensitivity = {
        -- sighting mirror
        ADS = 100,
    },
    -- CPU load level, It is recommended to enter a number between 1 and 30, cannot be less than 1.
    cpuLoad = 10,
    fireArms = {
        -- mode：0 - disable | 1 - enable | 2 - burst
		-- set rate
		-- no attachments
        ["M416"] = {"M416", 1, 0.95, 1.25},
        ["Beryl M762"] = {"Beryl M762", 1, 0.95, 1.25},
        ["SCAR-L"] = {"SCAR-L", 1, 0.95, 1.25},
        ["AKM"] = {"AKM", 1, 0.95, 1.5},
        ["M249"] = {"M249", 1, 0.6, 1},
        ["MG3"] = {"MG3", 1, 0.5, 1.25},
        ["MINI14"] = {"MINI14", 2, 0.95, 1.15},
        ["MK47"] = {"MK47", 2, 0.95, 1.2},
        ["MK14"] = {"MK14", 1, 0.75, 1.45},
    },
}

pubg = {
    gunOptions = {},
	counter = 0, -- 计数器
	xCounter = 0, -- x计数器
	sleep = userInfo.cpuLoad, -- 频率设置 (这里不能设置成0，调试会出BUG)
	sleepRandom = { userInfo.cpuLoad, userInfo.cpuLoad + 5 }, -- 防检测随机延迟
	startTime = 0, -- 鼠标按下时记录脚本运行时间戳
	prevTime = 0, -- 记录上一轮脚本运行时间戳
	generalSensitivityRatio = userInfo.sensitivity.ADS / 100, -- 按比例调整灵敏度
	onFire = false, -- 是否是启动状态
	currentTime = 0, -- 此刻
	bulletIndex = 0, -- 第几颗子弹
}

pubg["MK47"] = function ()
	return pubg.execOptions("MK47", {
		interval = 110,
		ballistic = {
			{1, 0},
			{5, 20},
			{46, 22},
		}
	})
end


pubg["SCAR-L"] = function ()
	return pubg.execOptions("SCAR-L", {
		interval = 96,
		ballistic = {
			{1, 0},
			{2, 33},
			{5, 22},
			{10, 25},
			{20, 30},
			{40, 33},
		}
	})
end

pubg["Beryl M762"] = function ()
	return pubg.execOptions("Beryl M762", {
		interval = 86,
		ballistic = {
			{1, 0},
			{2, 44},
			{3, 24},
			{5, 28},
			{10, 33},
			{15, 45},
			{25, 47},
			{40, 51},
		}
	})
end

pubg["AKM"] = function ()
	return pubg.execOptions("AKM", {
		interval = 99,
		ballistic = {
			{1, 0},
			{2, 42},
			{5, 25},
			{10, 30},
			{20, 40},
			{30, 43},
			{40, 45},
		}
	})
end

pubg["M416"] = function ()
	return pubg.execOptions("M416", {
		interval = 85,
		ballistic = {
			{1, 0},
			{2, 35},
			{4, 18},
			{10, 24},
			{15, 32},
			{30, 32},
			{40, 37},
		}
	})
end

pubg["MINI14"] = function ()
	return pubg.execOptions("MINI14", {
		interval = 110,
		ballistic = {
			{1, 0},
			{3, 30},
			{4, 40},
			{34, 50},
		}
	})
end

pubg["MG3"] = function ()
	return pubg.execOptions("MG3", {
		interval = 91,
		ballistic = {
			{1, 0},
			{2, 28},
			{5, 16},
			{8, 18},
			{15, 26},
			{90, 32},
		}
	})
end

pubg["M249"] = function ()
	return pubg.execOptions("M249", {
		interval = 75,
		ballistic = {
			{1, 0},
			{2, 28},
			{5, 24},
			{8, 26},
			{15, 30},
			{150, 23},
		}
	})
end

pubg["MK14"] = function ()
	return pubg.execOptions("MK14", {
		interval = 90,
		ballistic = {
			{1, 0},
			{3, 23},
			{6, 34},
			{10, 38},
			{24, 47},
		}
	})
end

--[[ FormatFactory ]]
function pubg.execOptions (gunName, options)

	--[[
		from
		{
			{ 5, 10 },
			{ 10, 24 },
		}
		to
		{ 10, 10, 10, 10, 10, 24, 24, 24, 24, 24 }
		to
		{ 10, 20, 30, 40, 50, 74, 98, 122, 146, 170 }
	]]

    OutputLogMessage(gunName)
    OutputLogMessage("\t")
	-- Temporary container
	local ballisticConfig1 = {}
	-- Temporary container (v3.0)
	local ballisticConfig2 = {}

	local ballisticIndex = 1
	for i = 1, #options.ballistic do
		local nextCount = options.ballistic[i][1]
		if i ~= 1 then
			nextCount = options.ballistic[i][1] - options.ballistic[i - 1][1]
		end
		for j = 1, nextCount do
			ballisticConfig1[ballisticIndex] =
				-- options.ballistic[i][2] * pubg.generalSensitivityRatio * options.ratio
				options.ballistic[i][2] * pubg.generalSensitivityRatio
			ballisticIndex = ballisticIndex + 1
		end
	end

	for i = 1, #ballisticConfig1 do
		if i == 1 then
			ballisticConfig2[i] = ballisticConfig1[i]
		else
			ballisticConfig2[i] = ballisticConfig2[i - 1] + ballisticConfig1[i]
		end
	end

	return {
		duration = options.interval * #ballisticConfig2, -- Time of duration
		amount = #ballisticConfig2, -- Number of bullets
		interval = options.interval, -- Time of each bullet
		ballistic = ballisticConfig2, -- ballistic data
		ctrlModeRatio = userInfo.fireArms[gunName][3], -- Individual recoil coefficient for each gun when squatting
		nudeModeRatio = userInfo.fireArms[gunName][4], -- Individual recoil coefficient for each gun without attachments
		autoContinuousFiring = math.max(0, userInfo.fireArms[gunName][2] - 1), -- auto continuous firing
	}
end

--[[ Initialization of firearms database ]]
function pubg.init ()
	-- Clean up the firearms Depot
	local forList = { "M416", "Beryl M762", "SCAR-L", "AKM", "MK47", "MINI14","MG3","M249","MK14"}
	for i = 1, #forList do
        local gunName = forList[i]
        local gunState = userInfo.fireArms[gunName][2]
        if gunState >= 1 then
            pubg.gunOptions[gunName] = pubg[gunName]() -- Get firearms data and add it to the configuration library
        end
	end

	-- Initial setting of random number seeds
	pubg.SetRandomseed()
end

function pubg.SetRandomseed ()
	math.randomseed((pubg.isEffective and {GetRunningTime()} or {0})[1])
end

function pubg.auto (options)

	-- Accurate aiming press gun
	pubg.currentTime = GetRunningTime()
	pubg.bulletIndex = math.ceil(((pubg.currentTime - pubg.startTime == 0 and {1} or {pubg.currentTime - pubg.startTime})[1]) / options.interval) + 1

	if pubg.bulletIndex > options.amount then return false end
	-- Developer Debugging Mode


	local y = math.ceil((pubg.currentTime - pubg.startTime) / (options.interval * (pubg.bulletIndex - 1)) * options.ballistic[pubg.bulletIndex]) - pubg.counter
	-- 4-fold pressure gun mode
	local realY = pubg.getRealY(options, y, switch)
	-- OutputLogMessage("\t")

	pubg.counter = pubg.counter + y

	MoveMouseRelative(0, realY)
	-- Whether to issue automatically or not
	if options.autoContinuousFiring == 1 then
		PressAndReleaseMouseButton(1)
	end

	-- Real-time operation parameters
	pubg.autoSleep()

end

--[[ get real y position ]]
function pubg.getRealY (options, y)
	local realY = y * pubg.generalSensitivityRatio
    if IsModifierPressed("ctrl") then
        realY = realY * options.ctrlModeRatio
    end
    if IsModifierPressed("lshift") then
        realY = realY * 1.4
    end
    if switch == 2 then
        realY = realY * options.nudeModeRatio
    end
    return realY
end

--[[ Sleep of pubg.auto ]]
function pubg.autoSleep ()
	local random = math.random(pubg.sleep, pubg.sleep)
	Sleep(random)
end

function pubg.OnEvent_NoRecoil (fireMode)
	pubg.auto(pubg.gunOptions[fireMode])
end

--[[ Listener method ]]
function OnEvent (event, arg, family)

	-- OutputLogMessage("event = %s, arg = %s, family = %s\n", event, arg, family)
	-- console.log("event = " .. event .. ", arg = " .. arg .. ", family = " .. family)
	if event == "PROFILE_ACTIVATED" then
        pubg.GD = GetDate -- Setting aliases
        pubg.init() -- Script initialization
	    EnablePrimaryMouseButtonEvents(true) -- Enable left mouse button event reporting
	    index = 3
	end

    if event == "M_PRESSED" and arg == 1 and pubg.onFire then
        pubg.OnEvent_NoRecoil(fireMode)
        SetMKeyState(1, "kb")
    end

	if switch ~= 0 and pubg.onFire ~= true and event == "MOUSE_BUTTON_PRESSED" and arg == 1 then
		dofile('D:\config.lua')
		if fireMode ~= 'grenade' then
			OutputLogMessage(fireMode)
			pubg.onFire = true
			pubg.startTime = GetRunningTime()
			SetMKeyState(1, "kb")
		end
	end

	if switch ~= 0 and event == "MOUSE_BUTTON_RELEASED" and arg == 1 then
	    pubg.onFire = false
	    pubg.counter = 0 -- Initialization counter
	end

    -- Switching arsenals according to different types of ammunition
    -- press mouse key back
    if event == "MOUSE_BUTTON_PRESSED" and arg == 4 then
        switch = 2
    end
    -- press mouse key forward
    if event == "MOUSE_BUTTON_PRESSED" and arg == 5 then
        switch = 1
    end

    -- press mouse key mid
    if event == "MOUSE_BUTTON_PRESSED" and arg == 6 then
        index = 3
        switch = 0
    end
end
