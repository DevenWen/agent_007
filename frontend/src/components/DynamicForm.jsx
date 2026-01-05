import React from "react";

/**
 * 动态表单组件
 * 根据 JSON Schema 渲染表单
 * 
 * @param {Object} props
 * @param {Object} props.schema JSON Schema 对象
 * @param {Object} props.value 表单值对象
 * @param {Function} props.onChange 值变更回调 (newValue) => void
 */
export default function DynamicForm({ schema, value = {}, onChange }) {
    if (!schema || !schema.properties) {
        return (
            <div className="p-4 bg-yellow-50 text-yellow-700 rounded-md text-sm">
                No schema properties definition found.
            </div>
        );
    }

    const handleChange = (key, val) => {
        onChange({
            ...value,
            [key]: val,
        });
    };

    const renderField = (key, fieldSchema) => {
        const isRequired = schema.required && schema.required.includes(key);
        const label = key; // 可以扩展支持 fieldSchema.title
        const description = fieldSchema.description;
        const type = fieldSchema.type;
        const currentValue = value[key] !== undefined ? value[key] : "";

        // 渲染不同类型的输入框
        let inputEl;

        if (type === "string") {
            inputEl = (
                <input
                    type="text"
                    id={key}
                    value={currentValue}
                    onChange={(e) => handleChange(key, e.target.value)}
                    required={isRequired}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white px-3 py-2 border"
                    placeholder={description}
                />
            );
        } else if (type === "integer" || type === "number") {
            inputEl = (
                <input
                    type="number"
                    id={key}
                    value={currentValue}
                    onChange={(e) => handleChange(key, type === "integer" ? parseInt(e.target.value) : parseFloat(e.target.value))}
                    required={isRequired}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white px-3 py-2 border"
                />
            );
        } else if (type === "boolean") {
            inputEl = (
                <div className="mt-1">
                    <label className="inline-flex items-center cursor-pointer">
                        <input
                            type="checkbox"
                            checked={!!currentValue}
                            onChange={(e) => handleChange(key, e.target.checked)}
                            className="sr-only peer"
                        />
                        <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 dark:peer-focus:ring-indigo-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-indigo-600"></div>
                    </label>
                </div>
            )
        } else if (type === "object") {
            // 简单的嵌套对象支持 - 使用 JSON 文本域作为回退，或递归调用
            // 为保持简单，暂用 JSON textarea
            inputEl = (
                <textarea
                    id={key}
                    value={typeof currentValue === 'object' ? JSON.stringify(currentValue, null, 2) : currentValue}
                    onChange={(e) => {
                        try {
                            const parsed = JSON.parse(e.target.value);
                            handleChange(key, parsed);
                        } catch (err) {
                            // 允许临时无效 JSON，但可能需要 state 区分 text 和 object
                            // 这里简化处理
                        }
                    }}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white px-3 py-2 border font-mono"
                    rows={3}
                />
            )
        } else {
            // Fallback
            inputEl = (
                <input
                    type="text"
                    id={key}
                    value={currentValue}
                    onChange={(e) => handleChange(key, e.target.value)}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
                />
            );
        }

        return (
            <div key={key} className="mb-4">
                <label
                    htmlFor={key}
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300"
                >
                    {label} {isRequired && <span className="text-red-500">*</span>}
                </label>
                {description && (
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 mb-1">
                        {description}
                    </p>
                )}
                {inputEl}
            </div>
        );
    };

    return <div className="space-y-2">{Object.keys(schema.properties).map((key) => renderField(key, schema.properties[key]))}</div>;
}
