# streamdepletr/models.py

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
from scipy.special import erfc

# 定义Glover函数
def glover(t, d, S, Tr):
    return erfc(np.sqrt(S * d**2 / (4 * Tr * t)))

def apportion_web(reach_dist, w, max_dist=float('inf'), min_frac=0, reach_name=None, dist_name=None):
    if reach_name is not None:
        reach_dist = reach_dist.rename(columns={reach_name: "reach"})
    if dist_name is not None:
        reach_dist = reach_dist.rename(columns={dist_name: "dist"})
    reach_dist = reach_dist[reach_dist['dist'] <= max_dist]
    reach_dist['frac_depletion_pt'] = (1 / reach_dist['dist']**w) / sum(1 / reach_dist['dist']**w)
    df_out = reach_dist.groupby('reach').agg(frac_depletion=('frac_depletion_pt', 'sum')).reset_index()
    if df_out['frac_depletion'].min() < min_frac:
        depl_low = df_out['frac_depletion'][df_out['frac_depletion'] < min_frac].sum()
        df_out = df_out[df_out['frac_depletion'] >= min_frac]
        df_out['frac_depletion'] += depl_low * (df_out['frac_depletion'] / (1 - depl_low))
    return df_out

def depletion_max_distance(Qf_thres=0.01, d_interval=100, d_min=None, d_max=5000, method="glover", t=None, S=None, Tr=None):
    Qf = 1
    if d_min is None:
        d_min = d_interval
    d_test = d_min
    while Qf > Qf_thres:
        if method == "glover":
            Qf = glover(t, d_test, S, Tr)
        else:
            raise ValueError("Invalid method")
        if Qf < Qf_thres:
            if d_test == d_min:
                print("Warning: Qf < Qf_thres at distance d_min")
                return d_min
            else:
                return d_test - d_interval
        d_test += d_interval
        if d_test > d_max:
            print(f"Warning: Maximum distance reached; Qf = {round(Qf, 4)} @ d = {d_test - d_interval}")
            return d_max

def apportion_polygon(reach_dist, wel_lon, wel_lat, coord_crs, reach_name="reach", dist_name="dist", lon_name="lon", lat_name="lat", min_frac=0):
    gdf = gpd.GeoDataFrame(reach_dist, geometry=gpd.points_from_xy(reach_dist[lon_name], reach_dist[lat_name]), crs=coord_crs)
    well_point = gpd.GeoDataFrame(geometry=[Point(wel_lon, wel_lat)], crs=coord_crs)
    gdf['distance'] = gdf.geometry.distance(well_point.geometry[0])
    gdf = gdf[gdf['distance'] <= gdf['distance'].quantile(1 - min_frac)]
    gdf['frac_depletion'] = 1 / gdf['distance']**2 / (1 / gdf['distance']**2).sum()
    return gdf[[reach_name, 'frac_depletion']]

def intermittent_pumping(t, starts, stops, rates, method='glover', d=None, S=None, Tr=None, **kwargs):
    starts_all = np.tile(starts, (len(t), 1))
    stops_all = np.tile(stops, (len(t), 1))
    rates_all = np.tile(rates, (len(t), 1))
    t_all = np.tile(t[:, np.newaxis], (1, len(starts)))

    t_starts = t_all - starts_all
    t_starts[t_starts < 0] = 0

    t_stops = t_all - stops_all
    t_stops[t_stops < 0] = 0

    t_starts_vec = t_starts.flatten()
    t_stops_vec = t_stops.flatten()
    rates_all_vec = rates_all.flatten()
    Qs_all_vec = np.zeros_like(t_starts_vec)

    if method == 'glover':
        mask = t_starts_vec > 0
        Qs_all_vec[mask] = rates_all_vec[mask] * (
            glover(t_starts_vec[mask], d, S, Tr) - glover(t_stops_vec[mask], d, S, Tr)
        )
    else:
        raise ValueError("Unsupported method: {}".format(method))

    Qs_all = Qs_all_vec.reshape(t_all.shape)
    Q_out = np.sum(Qs_all, axis=1)
    return Q_out
