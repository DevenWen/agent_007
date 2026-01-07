import { useState, useEffect } from 'react'
import { api } from '../api/client'

export default function SkillsPage() {
    const [skills, setSkills] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedSkill, setSelectedSkill] = useState(null)

    useEffect(() => {
        loadSkills()
    }, [])

    const loadSkills = async () => {
        try {
            const data = await api.listSkills()
            setSkills(data)
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const loadSkillDetail = async (name) => {
        try {
            const data = await api.getSkill(name)
            setSelectedSkill(data)
        } catch (err) {
            console.error(err)
        }
    }

    if (loading) {
        return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>
    }

    return (
        <div className="flex gap-6">
            {/* Skill List */}
            <div className="flex-1 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {skills.length === 0 ? (
                    <div className="text-center py-12 text-slate-400 col-span-full">
                        No skills found. Add .md files to backend/prompt/skill/
                    </div>
                ) : (
                    skills.map(skill => (
                        <div
                            key={skill.name}
                            onClick={() => loadSkillDetail(skill.name)}
                            className={`bg-slate-800 rounded-xl p-5 border cursor-pointer transition ${selectedSkill?.name === skill.name
                                ? 'border-indigo-500'
                                : 'border-slate-700 hover:border-slate-600'
                                }`}
                        >
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-lg">
                                    🎯
                                </div>
                                <h3 className="font-semibold">{skill.name}</h3>
                            </div>
                            <p className="text-sm text-slate-400 line-clamp-2">{skill.description || 'No description'}</p>
                            {skill.tools && skill.tools.length > 0 && (
                                <div className="mt-3 flex flex-wrap gap-1">
                                    {skill.tools.slice(0, 3).map(tool => (
                                        <span key={tool} className="px-2 py-0.5 bg-slate-700 rounded text-xs text-slate-300">
                                            {tool}
                                        </span>
                                    ))}
                                    {skill.tools.length > 3 && (
                                        <span className="px-2 py-0.5 bg-slate-700 rounded text-xs text-slate-400">
                                            +{skill.tools.length - 3}
                                        </span>
                                    )}
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>

            {/* Detail Panel */}
            {selectedSkill && (
                <div className="w-96 bg-slate-800 rounded-xl border border-slate-700 p-4 space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-lg">{selectedSkill.name}</h3>
                        <button onClick={() => setSelectedSkill(null)} className="text-slate-400 hover:text-white">✕</button>
                    </div>

                    {selectedSkill.description && (
                        <div>
                            <h4 className="text-sm font-medium text-slate-400 mb-2">Description</h4>
                            <p className="text-sm">{selectedSkill.description}</p>
                        </div>
                    )}

                    {selectedSkill.tools && selectedSkill.tools.length > 0 && (
                        <div>
                            <h4 className="text-sm font-medium text-slate-400 mb-2">
                                Tools ({selectedSkill.tools.length})
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {selectedSkill.tools.map(tool => (
                                    <span key={tool} className="px-2 py-1 bg-emerald-900/50 text-emerald-300 rounded text-xs">
                                        ⚡ {tool}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {selectedSkill.content && (
                        <div>
                            <h4 className="text-sm font-medium text-slate-400 mb-2">Prompt Content</h4>
                            <pre className="bg-slate-900 rounded p-3 text-sm whitespace-pre-wrap max-h-96 overflow-y-auto scroll-area">
                                {selectedSkill.content}
                            </pre>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
