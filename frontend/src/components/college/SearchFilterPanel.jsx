import React from 'react';
import { motion } from 'framer-motion';
import {Input} from '@components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Filter } from 'lucide-react';

export default function SearchFilterPanel() {
  return (
    <motion.div
      className="bg-white rounded-2xl shadow-lg shadow-purple-500/10 p-6"
    >
      <h3 className="text-lg font-bold text-gray-800 mb-4">Filter & Search Requests</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <Input
            type="text"
            placeholder="Search by student name or credential..."
            className="pl-10 py-3"
          />
        </div>

        {/* Filter Dropdown */}
        <div className="relative flex items-center">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <Select>
                <SelectTrigger className="w-full pl-10 py-3">
                    <SelectValue placeholder="Filter by Course Type" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="cs">Computer Science</SelectItem>
                    <SelectItem value="eng">Engineering</SelectItem>
                    <SelectItem value="arts">Arts & Humanities</SelectItem>
                </SelectContent>
            </Select>
        </div>
      </div>
    </motion.div>
  );
}