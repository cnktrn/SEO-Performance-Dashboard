import Dashboard from "../models/dashboard.js";

export const getDashboards = async (req,res) => {
    try {
        const dbDashboards = await Dashboard.find();
        res.status(200).json(dbDashboards);
    } catch (error) {
        res.status(404).json({ message: error.message });
    }
}

export const getDashboard = async (req, res) => {
    const id = req.body.id;
    try {
        const dashboard = await Dashboard.findById(id);
        res.status(200).json(dashboard);
        if (dashboard.userWhiteList.includes(req.headers.username)) {
            res.status(200).json(dashboard);
        } else {
            res.status(401);
        }
    } catch (error) {
        res.status(404).json({ message: error.message });
    }
}

export const createDashboard = async (req,res) => {
    const dashboard = req.body;
    const username = req.headers.username;

    const newDashboard = new Dashboard({"dashboardName": dashboard.dashboardName, "dataSource": dashboard.dataSource, "KPIs": dashboard.KPIs, "userWhiteList": [username], "creator": username})
    try {
        await newDashboard.save();
        res.status(201).json(newDashboard);
    } catch (error) {
        res.status(409).json({ message: error.message });
    }
}

export const updateDashboard = async (req, res) => {
    const id = req.body.id;
    const dashboard = req.body;
    try {
        const curDash = await Dashboard.findById(id);
        if (curDash.creator === req.username) {
            const updatedDash = await Dashboard.findByIdAndUpdate(id, dashboard);
            res.status(200).json(updatedDash);
        } else {
            res.status(401);
        }
    } catch (error) {
        res.status(404).json({ message: error.message });
    }
}

export const deleteDashboard = async (req, res) => {
    const id = req.body.id;
    try {
        const dashboard = await Dashboard.findById(id);
        if (dashboard.creator === req.username) {
            await Dashboard.findByIdAndDelete(id);
            res.status(200).json({ message: "successfully deleted dashboard"});
        } else {
            res.status(401);
        }
    } catch (error) {
        res.status(404).json({ message: error.message });
    }
}


