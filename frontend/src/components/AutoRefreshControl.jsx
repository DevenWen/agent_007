import React, { useState, useEffect } from "react";

/**
 * 自动刷新控制组件
 * @param {Object} props
 * @param {Function} props.onRefresh 刷新回调函数
 * @param {number} props.interval 刷新间隔（秒），默认 5
 */
export default function AutoRefreshControl({ onRefresh, interval = 5 }) {
    const [enabled, setEnabled] = useState(true);
    const [timeLeft, setTimeLeft] = useState(interval);

    useEffect(() => {
        let timer = null;
        let countdownTimer = null;

        if (enabled) {
            // 倒计时逻辑
            countdownTimer = setInterval(() => {
                setTimeLeft((prev) => {
                    if (prev <= 1) {
                        return interval;
                    }
                    return prev - 1;
                });
            }, 1000);

            // 刷新逻辑 - 使用单独的定时器或者在倒计时归零时触发
            // 这里为了精准控制，我们在倒计时归零时触发刷新
            // 但是 React state update 可能是异步的，所以依赖 interval
        }

        return () => {
            if (countdownTimer) clearInterval(countdownTimer);
        };
    }, [enabled, interval]);

    // 使用另一个 effect 来监听 timeLeft 变化触发刷新
    useEffect(() => {
        if (enabled && timeLeft === interval) {
            // 当倒计时重置为 interval 时，说明刚刚倒数完（或者刚开始）
            // 但刚开始不需要刷新，所以我们需要区分
            // 简单做法：只在 setInterval 里处理
        }
    }, [timeLeft, enabled, interval]);

    // 修正逻辑：使用单一 interval 处理倒计时和刷新
    useEffect(() => {
        if (!enabled) return;

        const timer = setInterval(() => {
            setTimeLeft((prev) => {
                if (prev <= 1) {
                    onRefresh(); // 触发刷新
                    return interval;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, [enabled, interval, onRefresh]);


    const toggle = () => {
        setEnabled(!enabled);
        if (!enabled) {
            setTimeLeft(interval);
            onRefresh(); // 开启时立即刷新一次
        }
    };

    return (
        <div className="flex items-center space-x-2 bg-white dark:bg-gray-800 rounded-lg shadow px-3 py-1.5 border border-gray-200 dark:border-gray-700">
            <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">
                Auto: {enabled ? `${timeLeft}s` : "OFF"}
            </span>

            <button
                onClick={toggle}
                className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${enabled ? "bg-indigo-600" : "bg-gray-200 dark:bg-gray-700"
                    }`}
            >
                <span
                    className={`${enabled ? "translate-x-4" : "translate-x-1"
                        } inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform`}
                />
            </button>
        </div>
    );
}
