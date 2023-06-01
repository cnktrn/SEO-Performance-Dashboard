import express from "express";
import {getDashboards, createDashboard, getDashboard} from "../controllers/dashboards.js";

const router = express.Router();

router.get("/getDashboards", getDashboards);
router.post("/createDashboard", createDashboard);
router.get("/getDashboard", getDashboard);

export default router;